from core.utils import *
from datetime import datetime
import logging
import concurrent.futures

name          = "portscan"
description   = "Scan ports of the target"
author        = "Swissky"
documentation = []

class exploit():

    def __init__(self, requester, args):
        logging.info("Module '{}' launched !".format(name))
        r = requester.do_request(args.param, "")

        load_ports = ""
        with open("data/ports", "r") as f:
            load_ports = f.readlines()

        # We can use a with statement to ensure threads are cleaned up promptly
        with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
            future_to_url = {executor.submit(self.concurrent_request, requester, args.param, "127.0.0.1", port): port for port in load_ports}


    def concurrent_request(self, requester, param, host, port):
        try:
            payload = wrapper_http("", host, port.strip())
            r = requester.do_request(param, payload)
        
            # Display Open port
            if not "Connection refused" in r.text:
                timer = datetime.today().time().replace(microsecond=0)
                port = port.strip() + " "*20
                print("\t[{}] Found port n°{}".format(timer, port))

            timer = datetime.today().time().replace(microsecond=0)
            port = port.strip() + " "*20
            print("\t[{}] Checking port n°{}".format(timer, port), end='\r'),
        
        # Timeout is a potential port
        except Exception as e:
            timer = datetime.today().time().replace(microsecond=0)
            port = port.strip() + " "*20
            print("\t[{}] Timeout port n°{}".format(timer, port))
            pass