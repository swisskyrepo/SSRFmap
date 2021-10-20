import json
import logging
import re
import urllib.parse
from urllib.parse import urlparse

import requests
from levo_commons.models import Interaction
from levo_commons.status import Status
from requests.structures import CaseInsensitiveDict


class Requester(object):
    protocol = "http"
    host = ""
    method = ""
    action = ""
    headers: CaseInsensitiveDict = CaseInsensitiveDict()
    data: dict[str, str] = {}
    interactions: list[Interaction] = []

    def __init__(self, path, uagent, ssl):
        try:
            # Read file request
            with open(path, "r") as f:
                content = f.read().strip()
        except IOError as e:
            logging.error("File not found")
            exit()

        try:
            content = content.split("\n\n", 1)
            request_line = content[0].split("\n", 1)[0]
            headers = content[0].split("\n")[1:]
            body = content[1] if len(content) == 2 else None

            regex = re.compile("(.*) (.*) HTTP")
            self.method, self.action = regex.findall(request_line)[0]
            url = urlparse(self.action)
            if url.path != self.action:
                self.action = url.path
                self.headers["Host"] = url.netloc

            for header in headers:
                name, _, value = header.partition(": ")
                if not name or not value:
                    continue
                self.headers[name] = value
            self.host = self.headers["Host"]

            # Parse user-agent
            if uagent is not None:
                self.headers["User-Agent"] = uagent

            # Parse data
            self.data_to_dict(body)

            # Handling HTTPS requests
            if ssl:
                self.protocol = "https"

        except Exception as e:
            logging.warning(f"Bad Format or Raw data: {e}")
            exit()

    def data_to_dict(self, data):
        if data is None:
            return {}

        if self.method == "POST":

            # Handle JSON data
            if (
                self.headers["Content-Type"]
                and "application/json" in self.headers["Content-Type"]
            ):
                self.data = json.loads(data)

            # Handle XML data
            elif (
                self.headers["Content-Type"]
                and "application/xml" in self.headers["Content-Type"]
            ):
                self.data["__xml__"] = data

            # Handle FORM data
            else:
                for arg in data.split("&"):
                    regex = re.compile("(.*)=(.*)")
                    for name, value in regex.findall(arg):
                        name = urllib.parse.unquote(name)
                        value = urllib.parse.unquote(value)
                        self.data[name] = value

    def do_request(self, param, value, timeout=3, stream=False):
        try:
            if self.method == "POST":
                # Copying data to avoid multiple variables edit
                data_injected = self.data.copy()

                if param in str(data_injected):  # Fix for issue/10 : str(data_injected)
                    data_injected[param] = value

                    # Handle JSON data
                    if (
                        self.headers["Content-Type"]
                        and "application/json" in self.headers["Content-Type"]
                    ):
                        r = requests.post(
                            self.protocol + "://" + self.host + self.action,
                            headers=self.headers,
                            json=data_injected,
                            timeout=timeout,
                            stream=stream,
                            verify=False,
                        )

                    # Handle FORM data
                    else:
                        r = requests.post(
                            self.protocol + "://" + self.host + self.action,
                            headers=self.headers,
                            data=data_injected,
                            timeout=timeout,
                            stream=stream,
                            verify=False,
                        )
                elif (
                    self.headers["Content-Type"]
                    and "application/xml" in self.headers["Content-Type"]
                    and "*FUZZ*" in data_injected["__xml__"]
                ):
                    # replace the injection point with the payload
                    data_xml = data_injected["__xml__"]
                    data_xml = data_xml.replace("*FUZZ*", value)

                    r = requests.post(
                        self.protocol + "://" + self.host + self.action,
                        headers=self.headers,
                        data=data_xml,
                        timeout=timeout,
                        stream=stream,
                        verify=False,
                    )
                else:
                    raise Exception("No injection point found.")
            else:
                # String is immutable, we don't have to do a "forced" copy
                regex = re.compile(param + "=(\w+)")
                value = urllib.parse.quote(value, safe="")
                data_injected = re.sub(regex, param + "=" + value, self.action)
                r = requests.get(
                    self.protocol + "://" + self.host + data_injected,
                    headers=self.headers,
                    timeout=timeout,
                    stream=stream,
                    verify=False,
                )
        except Exception as e:
            logging.error(e)
            exit()
        self.interactions.append(
            Interaction.from_requests(
                r, Status.success if 200 <= r.status_code <= 299 else Status.error, []
            )
        )
        return r

    def __str__(self):
        text = self.method + " "
        text += self.action + " HTTP/1.1\n"
        for header in self.headers:
            text += header + ": " + self.headers[header] + "\n"

        text += "\n\n"
        for data in self.data:
            text += data + "=" + self.data[data] + "&"
        return text[:-1]
