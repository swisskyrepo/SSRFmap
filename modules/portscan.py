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
        logging.info(f"Module '{name}' launched !")
        r = requester.do_request(args.param, "")

        load_ports = ""
        with open("data/ports", "r") as f:
            load_ports = f.readlines()

        # Using a generator to create the host list
        gen_host = gen_ip_list("127.0.0.1", args.level)
        for ip in gen_host:
            # We can use a with statement to ensure threads are cleaned up promptly
            with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
                future_to_url = {executor.submit(self.concurrent_request, requester, args.param, ip, port, r): port for port in load_ports}


    def concurrent_request(self, requester, param, host, port, compare):
        try:
            payload = wrapper_http("", host, port.strip())
            r = requester.do_request(param, payload)

            # Display Open port
            if r != None and not "Connection refused" in r.text:
                timer = datetime.today().time().replace(microsecond=0)
                port = port.strip() + " "*20

                # Check if the request is the same
                if r.text != '' and r.text != compare.text:
                    print(f"\t[{timer}] IP:{host:12s}, Found \033[32mopen     \033[0m port n°{port}")
                else:
                    print(f"\t[{timer}] IP:{host:12s}, Found \033[31mfiltered\033[0m  port n°{port}")

            timer = datetime.today().time().replace(microsecond=0)
            port = port.strip() + " "*20
            print(f"\t[{timer}] Checking port n°{port}", end='\r'),
        
        # Timeout is a potential port
        except Exception as e:
            print(e)
            timer = datetime.today().time().replace(microsecond=0)
            port = port.strip() + " "*20
            print(f"\t[{timer}] IP:{host:212}, \033[33mTimed out\033[0m  port n°{port}")
            pass