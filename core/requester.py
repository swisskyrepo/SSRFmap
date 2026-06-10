import re
import json
import requests
import logging
import urllib.parse

class Requester(object):
    protocol   = "http"
    host       = ""
    method     = ""
    action     = ""
    headers    = {}
    data       = {}

    def __init__(self, path, uagent, ssl, proxies):
        try:
            # Open file using utf-8-sig to drop Windows BOM if present
            with open(path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
        except IOError as e:
            logging.error("File not found")
            exit()

        try:
            # Normalize line endings
            content = content.replace('\r\n', '\n').replace('\r', '\n')
            raw_lines = content.split('\n')

            # Find the first line that isn't purely empty whitespace
            start_index = None
            for idx, line in enumerate(raw_lines):
                if line.strip() != '':
                    start_index = idx
                    break

            if start_index is None:
                logging.error("The request file appears to be empty or contains only blank lines.")
                exit()

            # Target the first valid HTTP request line
            request_line = raw_lines[start_index].strip()
            regex = re.compile('(.*) (.*) HTTP')
            self.method, self.action = regex.findall(request_line)[0]

            # Parse headers — stop at the subsequent blank line inside raw request block
            header_end = len(raw_lines) - 1
            for i in range(start_index + 1, len(raw_lines)):
                line = raw_lines[i]
                if line.strip() == '':
                    header_end = i
                    break
                name, _, value_header = line.partition(': ')
                if not name or not value_header:
                    continue
                self.headers[name.strip()] = value_header.strip()
            self.host = self.headers['Host']

            # Parse user-agent
            if uagent != None:
                self.headers['User-Agent'] = uagent

            # Extract full multi-line body precisely after the blank line following headers
            body = '\n'.join(raw_lines[header_end + 1:]).strip()

            # Parse data
            self.data_to_dict(body)

            # Handling HTTPS requests
            if ssl == True:
                self.protocol = "https"

            self.proxies = proxies

        except Exception as e:
            logging.warning("Bad Format or Raw data !")


    def data_to_dict(self, data):
        if self.method == "POST":
            content_type = self.headers.get('Content-Type', '')

            # Handle JSON data
            if content_type and "application/json" in content_type:
                self.data = json.loads(data)

            # Handle XML data
            elif content_type and "application/xml" in content_type:
                self.data['__xml__'] = data

            # Handle Multipart data
            elif content_type and "multipart/form-data" in content_type:
                self.data['__multipart_raw__'] = data
                boundary_match = re.search(r'boundary=([^\s;]+)', content_type)
                if boundary_match:
                    self._parse_multipart(data, boundary_match.group(1))
                else:
                    logging.warning("multipart/form-data detected but no boundary found in Content-Type")

            # Handle FORM data
            else:
                if data:
                    for arg in data.split("&"):
                        regex = re.compile('(.*)=(.*)')
                        for name, val in regex.findall(arg):
                            name = urllib.parse.unquote(name.strip())
                            val = urllib.parse.unquote(val.strip())
                            self.data[name] = val


    def _parse_multipart(self, body, boundary):
        delimiter = '--' + boundary
        parts = body.split(delimiter)

        for part in parts:
            stripped = part.strip()
            if not stripped or stripped == '--':
                continue

            # Split per-part headers from the part body payload
            if '\n\n' in part:
                part_headers_raw, part_body = part.split('\n\n', 1)
            elif '\r\n\r\n' in part:
                part_headers_raw, part_body = part.split('\r\n\r\n', 1)
            else:
                continue

            name_match = re.search(r'name="([^"]+)"', part_headers_raw)
            if name_match:
                field_name  = name_match.group(1)
                field_value = part_body.rstrip('\r\n-')
                self.data[field_name] = field_value


    def do_request(self, param, value, timeout=3, stream=False):
        try:
            # Debug information
            logging.debug(f"Request param: {param}")
            logging.debug(f"Request value: {value}")
            logging.debug(f"Request timeout: {timeout}")

            # Handle injection in the headers
            # Copying data to avoid multiple variables edit
            header_injected = self.headers.copy()
            if param in header_injected:
                header_injected[param] = value
                logging.debug("Request inject: Injecting payload in HTTP Header")

            logging.debug(f"Request method: {self.method}")
            if self.method == "POST":

                # Copying data to avoid multiple variables edit
                data_injected = self.data.copy()
                content_type = self.headers.get('Content-Type', '')

                # For multipart, param validation happens inside the branch
                # because the raw body is rebuilt directly rather than via data_injected
                if content_type and "multipart/form-data" not in content_type:
                    if param not in data_injected:
                        logging.error("No injection point found ! (use -p)")
                        exit(1)
                    data_injected[param] = value

                # Handle JSON data
                if content_type and "application/json" in content_type:
                    logging.debug("Request type: JSON")
                    logging.debug(f"Request data: {data_injected}")

                    r = requests.post(
                        self.protocol + "://" + self.host + self.action,
                        data=json.dumps(data_injected),
                        headers=header_injected,
                        timeout=timeout,
                        stream=stream,
                        verify=False,
                        proxies=self.proxies
                    )

                # Handle XML data
                elif content_type and "application/xml" in content_type:
                    logging.debug("Request type: XML")

                    if "__xml__" in data_injected and "*FUZZ*" in data_injected['__xml__']:
                        logging.debug("Request inject: XML parameter")

                        # replace the injection point with the payload
                        data_xml = data_injected['__xml__']
                        data_xml = data_xml.replace('*FUZZ*', value)

                        logging.debug(f"Request data: {data_xml}")
                        r = requests.post(
                            self.protocol + "://" + self.host + self.action,
                            data=data_xml,
                            headers=header_injected,
                            timeout=timeout,
                            stream=stream,
                            verify=False,
                            proxies=self.proxies
                        )

                    else:
                        logging.error("No injection point found ! (use -p)")
                        exit(1)

                # Handle Multipart data
                elif content_type and "multipart/form-data" in content_type:
                    logging.debug("Request type: multipart/form-data")
                    boundary_match = re.search(r'boundary=([^\s;]+)', content_type)
                    if not boundary_match:
                        logging.error("Could not find boundary in Content-Type header")
                        exit(1)
                    boundary = boundary_match.group(1)

                    raw_body = self.data.get('__multipart_raw__', '')
                    original_value = self.data.get(param, '')

                    # Surgical regex pattern ensures surrounding part headers/metadata remain intact
                    pattern = r'(name="{}"[^\n]*\n\s*\n)(.*?)(\s*--{})'.format(
                        re.escape(param), re.escape(boundary)
                    )

                    if re.search(pattern, raw_body, re.DOTALL):
                        multipart_body = re.sub(
                            pattern, r'\g<1>{}\3'.format(value), raw_body, flags=re.DOTALL
                        )
                    else:
                        # Direct fallback value substitution
                        multipart_body = raw_body.replace(original_value, value)

                    r = requests.post(
                        self.protocol + "://" + self.host + self.action,
                        data=multipart_body,
                        headers=header_injected,
                        timeout=timeout,
                        stream=stream,
                        verify=False,
                        proxies=self.proxies
                    )

                # Handle FORM data
                else:
                    if param == '':
                        logging.debug("Request inject: POST raw data")
                        post_data = value
                    else:
                        logging.debug("Request inject: POST parameter")
                        post_data = data_injected

                    r = requests.post(
                        self.protocol + "://" + self.host + self.action,
                        headers=header_injected,
                        data=post_data,
                        timeout=timeout,
                        stream=stream,
                        verify=False,
                        proxies=self.proxies
                    )

            else:
                logging.debug("Request inject: GET parameter")

                # String is immutable, we don't have to do a "forced" copy
                regex = re.compile(param + "=([^&]+)")
                value = urllib.parse.quote(value, safe='')
                data_injected = re.sub(regex, param + '=' + value, self.action)
                r = requests.get(
                    self.protocol + "://" + self.host + data_injected,
                    headers=header_injected,
                    timeout=timeout,
                    stream=stream,
                    verify=False,
                    proxies=self.proxies
                )
        except Exception as e:
            logging.debug(e)
            return None
        return r

    def __str__(self):
        text =  self.method + " "
        text += self.action + " HTTP/1.1\n"
        for header in self.headers:
            text += header + ": " + self.headers[header] + "\n"

        text += "\n"
        if isinstance(self.data, dict):
            # Omit the backing raw control structure from string outputs
            display_data = {k: v for k, v in self.data.items() if k != '__multipart_raw__'}
            for data in display_data:
                text += data + "=" + str(display_data[data]) + "&"
            return text[:-1]
        else:
            text += str(self.data)
            return text