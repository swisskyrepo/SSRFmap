import re
import requests
import logging
    
class Requester(object):
    host   = ""
    method = ""
    action = ""
    headers = {}
    data    = {}

    def __init__(self, path):
        try:
            # Read file request
            with open(path, 'r') as f:
                content = f.read().strip()
        except IOError as e:
            logging.error("File not found")
            return

        try:
            # Parse method and action URI
            regex = re.compile('(.*) (.*) HTTP')
            self.method, self.action = regex.findall(content)[0]

            # Parse headers
            content = content.split('\n')
            for header in content[1:-2]:
                name, value = header.split(': ')
                self.headers[name] = value
            self.host = self.headers['Host']
            
            # Parse data
            self.data_to_dict(content[-1])
        except Exception as e:
            logging.error("Bad Format")

    def data_to_dict(self, data):
        if self.method == "POST":
            for arg in data.split("&"):
                regex = re.compile('(.*)=(.*)')
                for name,value in regex.findall(arg):
                    self.data[name] = value


    def do_request(self, param, value):
        try:
            if self.method == "POST":
                # Copying data to avoid multiple variables edit
                data_injected = self.data.copy()
                if param in data_injected:
                    data_injected[param] = value
            
                    r = requests.post(
                        "http://" + self.host + self.action, 
                        headers=self.headers, 
                        data=data_injected,
                        timeout=3
                    )
            else:
                # String is immutable, we don't have to do a "forced" copy
                regex = re.compile(param+"=(\w+)")
                data_injected = re.sub(regex, param+'='+value, self.action)

                r = requests.get(
                    "http://" + self.host + data_injected, 
                    headers=self.headers,
                    timeout=3
                )
        except Exception as e:
            return None
        return r


    def __str__(self):
        text =  self.method + " "
        text += self.action + " HTTP/1.1\n"
        for header in self.headers:
            text += header + ": " + self.headers[header] + "\n"

        text += "\n\n"
        for data in self.data:
            text += data + "=" + self.data[data] + "&"
        return text[:-1]