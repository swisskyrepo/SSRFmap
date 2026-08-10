import json
import logging
import re
import urllib.parse
from email import policy
from email.parser import BytesParser

import requests

FUZZ_MARKER = "*FUZZ*"
BODY_METHODS = {"POST", "PUT"}


class Requester:
    def __init__(self, path, uagent, ssl, proxies):
        self.headers = {}
        self.data = {}
        self.body = b""
        self.protocol = "http"
        self.host = ""
        self.method = ""
        self.action = ""
        self.proxies = proxies
        self.media_type = ""
        self.multipart_boundary = None

        try:
            with open(path, "rb") as request_file:
                content = request_file.read()
        except OSError:
            logging.error("File not found")
            raise SystemExit from None

        try:
            header_block, self.body = self._split_message(content)
            self._parse_request_head(header_block)

            if uagent is not None:
                self._set_header("User-Agent", uagent)

            self.data_to_dict(self.body)

            if ssl is True:
                self.protocol = "https"
        except (KeyError, ValueError, UnicodeError, json.JSONDecodeError) as error:
            logging.warning("Bad request format: %s", error)

    @staticmethod
    def _split_message(content):
        for separator in (b"\r\n\r\n", b"\n\n"):
            if separator in content:
                return content.split(separator, 1)
        return content, b""

    def _parse_request_head(self, header_block):
        lines = re.split(rb"\r?\n", header_block)
        if not lines or not lines[0]:
            raise ValueError("missing request line")

        request_line = lines[0].decode("latin-1")
        match = re.fullmatch(r"([^\s]+)\s+([^\s]+)\s+HTTP/\d+(?:\.\d+)?", request_line)
        if match is None:
            raise ValueError("invalid request line")
        self.method, self.action = match.groups()
        self.method = self.method.upper()

        current_header = None
        for raw_line in lines[1:]:
            line = raw_line.decode("latin-1")
            if line[:1].isspace() and current_header is not None:
                self.headers[current_header] += " " + line.strip()
                continue

            name, separator, value = line.partition(":")
            if not separator or not name.strip():
                raise ValueError(f"invalid header line: {line!r}")
            current_header = name.strip()
            self.headers[current_header] = value.strip()

        self.host = self._get_header("Host")

    def _get_header(self, name, default=None):
        lowered_name = name.lower()
        for header_name, value in self.headers.items():
            if header_name.lower() == lowered_name:
                return value
        if default is not None:
            return default
        raise KeyError(name)

    def _set_header(self, name, value):
        lowered_name = name.lower()
        for header_name in self.headers:
            if header_name.lower() == lowered_name:
                self.headers[header_name] = value
                return
        self.headers[name] = value

    @staticmethod
    def _without_header(headers, name):
        lowered_name = name.lower()
        return {
            header_name: value
            for header_name, value in headers.items()
            if header_name.lower() != lowered_name
        }

    def _parse_content_type(self):
        content_type = self._get_header("Content-Type", "")
        if not content_type:
            return "", None

        message = BytesParser(policy=policy.default).parsebytes(
            f"Content-Type: {content_type}\r\n\r\n".encode("latin-1")
        )
        return message.get_content_type().lower(), message.get_boundary()

    @staticmethod
    def _multipart_part(segment):
        leading_length = 2 if segment.startswith(b"\r\n") else int(segment.startswith(b"\n"))
        part = segment[leading_length:]

        separator = b"\r\n\r\n"
        header_end = part.find(separator)
        if header_end < 0:
            separator = b"\n\n"
            header_end = part.find(separator)
        if header_end < 0:
            return None

        header_block = part[:header_end]
        message = BytesParser(policy=policy.default).parsebytes(header_block + b"\r\n\r\n")
        name = message.get_param("name", header="content-disposition")
        if name is None:
            return None

        value_start = leading_length + header_end + len(separator)
        value_end = len(segment)
        if segment.endswith(b"\r\n"):
            value_end -= 2
        elif segment.endswith(b"\n"):
            value_end -= 1

        charset = message.get_content_charset() or "utf-8"
        return name, value_start, value_end, charset

    def _parse_multipart(self, body):
        if not self.multipart_boundary:
            raise ValueError("multipart/form-data request has no boundary")

        delimiter = b"--" + self.multipart_boundary.encode("latin-1")
        if delimiter not in body:
            raise ValueError("multipart boundary is missing from the request body")

        fields = {}
        for segment in body.split(delimiter)[1:]:
            part = self._multipart_part(segment)
            if part is None:
                continue
            name, value_start, value_end, charset = part
            fields[name] = segment[value_start:value_end].decode(charset, errors="replace")
        return fields

    def _replace_multipart_field(self, name, value):
        delimiter = b"--" + self.multipart_boundary.encode("latin-1")
        segments = self.body.split(delimiter)
        replaced = False

        for index, segment in enumerate(segments[1:], start=1):
            part = self._multipart_part(segment)
            if part is None:
                continue
            part_name, value_start, value_end, charset = part
            if part_name == name:
                original = segment[value_start:value_end]
                marker = FUZZ_MARKER.encode(charset)
                payload = str(value).encode(charset)
                replacement = original.replace(marker, payload) if marker in original else payload
                segments[index] = segment[:value_start] + replacement + segment[value_end:]
                replaced = True

        if not replaced:
            raise ValueError(f"multipart field not found: {name}")
        return delimiter.join(segments)

    def data_to_dict(self, data):
        if self.method not in BODY_METHODS:
            return

        body = data if isinstance(data, bytes) else data.encode()
        self.media_type, self.multipart_boundary = self._parse_content_type()
        decoded_body = body.decode("utf-8", errors="replace")

        if self.media_type == "application/json" or self.media_type.endswith("+json"):
            self.data = json.loads(decoded_body)
        elif self.media_type in {"application/xml", "text/xml"} or self.media_type.endswith("+xml"):
            self.data["__xml__"] = decoded_body
        elif self.media_type == "multipart/form-data":
            self.data = self._parse_multipart(body)
        elif self.media_type in {"", "application/x-www-form-urlencoded"}:
            self.data = dict(
                urllib.parse.parse_qsl(decoded_body.rstrip("\r\n"), keep_blank_values=True)
            )
        else:
            self.data["__raw__"] = decoded_body

    @staticmethod
    def _inject_value(original, payload):
        if isinstance(original, str) and FUZZ_MARKER in original:
            return original.replace(FUZZ_MARKER, str(payload))
        return payload

    def _body_data(self, param, value):
        if self.media_type == "multipart/form-data":
            return self._replace_multipart_field(param, value)

        if self.media_type in {"application/xml", "text/xml"} or self.media_type.endswith("+xml"):
            xml = self.data["__xml__"]
            if param not in xml or FUZZ_MARKER not in xml:
                raise ValueError("No XML injection point found! Use *FUZZ* in the target field.")
            return xml.replace(FUZZ_MARKER, value)

        if param == "" and "__raw__" in self.data:
            return self._inject_value(self.data["__raw__"], value)

        if param not in self.data:
            raise ValueError(f"No injection point found for parameter: {param}")

        injected = self.data.copy()
        injected[param] = self._inject_value(injected[param], value)
        if self.media_type == "application/json" or self.media_type.endswith("+json"):
            return json.dumps(injected)
        return injected

    def do_request(self, param, value, timeout=3, stream=False):
        try:
            logging.debug("Request param: %s", param)
            logging.debug("Request value: %s", value)
            logging.debug("Request timeout: %s", timeout)

            header_injected = self.headers.copy()
            header_name = next(
                (name for name in header_injected if name.lower() == param.lower()),
                None,
            )
            if header_name is not None:
                header_injected[header_name] = self._inject_value(
                    header_injected[header_name], value
                )
                logging.debug("Injecting payload in HTTP header")

            logging.debug("Request method: %s", self.method)
            if self.method in BODY_METHODS:
                if header_name is not None and param not in self.data:
                    data_injected = self.body
                else:
                    data_injected = self._body_data(param, value)

                # Captured Content-Length values become invalid when a payload changes.
                # Let requests calculate the correct length for the outgoing body.
                outgoing_headers = self._without_header(header_injected, "Content-Length")
                request_function = requests.post if self.method == "POST" else requests.put
                return request_function(
                    self.protocol + "://" + self.host + self.action,
                    headers=outgoing_headers,
                    data=data_injected,
                    timeout=timeout,
                    stream=stream,
                    verify=False,
                    proxies=self.proxies,
                )

            if self.method != "GET":
                raise ValueError(f"Unsupported HTTP method: {self.method}")

            logging.debug("Injecting payload in GET parameter")
            encoded_value = urllib.parse.quote(value, safe="")
            pattern = re.compile(r"([?&])" + re.escape(param) + r"=([^&]*)")

            def replace_query_value(match):
                original = match.group(2)
                encoded_marker = urllib.parse.quote(FUZZ_MARKER, safe="")
                if FUZZ_MARKER in original:
                    injected = original.replace(FUZZ_MARKER, encoded_value)
                elif encoded_marker.lower() in original.lower():
                    injected = re.sub(
                        re.escape(encoded_marker),
                        encoded_value,
                        original,
                        flags=re.IGNORECASE,
                    )
                else:
                    injected = encoded_value
                return f"{match.group(1)}{param}={injected}"

            data_injected = pattern.sub(
                replace_query_value,
                self.action,
            )
            return requests.get(
                self.protocol + "://" + self.host + data_injected,
                headers=header_injected,
                timeout=timeout,
                stream=stream,
                verify=False,
                proxies=self.proxies,
            )
        except Exception as error:
            logging.error(error)
            return None

    def __str__(self):
        headers = "\n".join(f"{name}: {value}" for name, value in self.headers.items())
        body = self.body.decode("latin-1")
        return f"{self.method} {self.action} HTTP/1.1\n{headers}\n\n{body}"
