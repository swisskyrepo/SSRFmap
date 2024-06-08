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
            # Read file request
            with open(path, 'r') as f:
                content = f.read().strip()
        except IOError as e:
            logging.error("File not found")
            exit()

        try:
            content = content.split('\n')
            # Parse method and action URI
            regex = re.compile('(.*) (.*) HTTP')
            self.method, self.action = regex.findall(content[0])[0]

            # Parse headers
            for header in content[1:]:
                if header == '':
                    # edge-case, when data is sent raw (json/xml)
                    break
                name, _, value = header.partition(': ')
                if not name or not value:
                    continue
                self.headers[name] = value
            self.host = self.headers['Host']

            # Parse user-agent        
            if uagent != None:
                self.headers['User-Agent'] = uagent
            
            # Parse data
            self.data_to_dict(content[-1])

            # Handling HTTPS requests
            if ssl == True:
                self.protocol   = "https"
            
            self.proxies = proxies

        except Exception as e:
            logging.warning("Bad Format or Raw data !")


    def data_to_dict(self, data):
        if self.method == "POST":

            # Handle JSON data
            if self.headers['Content-Type'] and "application/json" in self.headers['Content-Type']:
                self.data = json.loads(data)

            # Handle XML data
            elif self.headers['Content-Type'] and "application/xml" in self.headers['Content-Type']:
                self.data['__xml__'] = data

            # Handle FORM data
            else:
                for arg in data.split("&"):
                    regex = re.compile('(.*)=(.*)')
                    for name,value in regex.findall(arg):
                        name = urllib.parse.unquote(name)
                        value = urllib.parse.unquote(value)
                        self.data[name] = value


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

                if param in str(data_injected): # Fix for issue/10 : str(data_injected)
                    data_injected[param] = value
            
                    # Handle JSON data
                    if self.headers['Content-Type'] and "application/json" in self.headers['Content-Type']:
                        logging.debug("Request type: JSON")
                        logging.debug(f"Request data: {data_injected}")

                        r = requests.post(
                            self.protocol + "://" + self.host + self.action, 
                            data=json.dumps(data_injected),
                            headers=self.headers,
                            timeout=timeout,
                            stream=stream,
                            verify=False,
                            proxies=self.proxies
                        )

                    # Handle XML data
                    elif self.headers['Content-Type'] and "application/xml" in self.headers['Content-Type']:
                        logging.debug("Request type: XML")

                        if "*FUZZ*" in data_injected['__xml__']:
                            logging.debug("Request inject: XML parameter")

                            # replace the injection point with the payload
                            data_xml = data_injected['__xml__']
                            data_xml = data_xml.replace('*FUZZ*', value)

                            logging.debug(f"Request data: {data_xml}")
                            r = requests.post(
                                self.protocol + "://" + self.host + self.action,
                                data=data_xml,
                                headers=self.headers,
                                timeout=timeout,
                                stream=stream,
                                verify=False,
                                proxies=self.proxies
                            )                            
                            
                        else:
                            logging.error("No injection point found ! (use -p)")
                            exit(1)  

                    # Handle FORM data
                    else:
                        if param == '': 
                            logging.debug("Request inject: POST raw data")
                            data_injected = value
                        else:
                            logging.debug("Request inject: POST parameter")

                        r = requests.post(
                            self.protocol + "://" + self.host + self.action, 
                            headers=header_injected, 
                            data=data_injected,
                            timeout=timeout,
                            stream=stream,
                            verify=False,
                            proxies=self.proxies
                        )

                else:
                    logging.error("No injection point found ! (use -p)")
                    exit(1)  
            else:
                logging.debug("Request inject: GET parameter")
                
                # String is immutable, we don't have to do a "forced" copy
                regex = re.compile(param+"=([^&]+)")
                value = urllib.parse.quote(value, safe='')
                data_injected = re.sub(regex, param+'='+value, self.action)
                r = requests.get(
                    self.protocol + "://" + self.host + data_injected, 
                    headers=header_injected,
                    timeout=timeout,
                    stream=stream,
                    verify=False,
                    proxies=self.proxies
                )
        except Exception as e:
            logging.error(e)
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
