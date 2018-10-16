"""
network scan 

╭─swissky@crashlab ~  
╰─$ curl -v "http://192.168.43.57"
* Rebuilt URL to: http://192.168.43.57/
*   Trying 192.168.43.57...
* TCP_NODELAY set
* connect to 192.168.43.57 port 80 failed: Connexion refusée
* Failed to connect to 192.168.43.57 port 80: Connexion refusée
* Closing connection 0
curl: (7) Failed to connect to 192.168.43.57 port 80: Connexion refusée
╭─swissky@crashlab ~  
╰─$ curl -v "http://192.168.43.56"                                                                                                                                          7 ↵
* Rebuilt URL to: http://192.168.43.56/
*   Trying 192.168.43.56...
* TCP_NODELAY set
* connect to 192.168.43.56 port 80 failed: Aucun chemin d'accès pour atteindre l'hôte cible
* Failed to connect to 192.168.43.56 port 80: Aucun chemin d'accès pour atteindre l'hôte cible
* Closing connection 0
curl: (7) Failed to connect to 192.168.43.56 port 80: Aucun chemin d'accès pour atteindre l'hôte cible
╭─swissky@crashlab ~  
"""
from core.utils import *
from datetime import datetime
import sys, struct, socket
import logging
import concurrent.futures

name        = "networkscan"
description = "Scan the network - HTTP Ping sweep"
author      = "Swissky"

class exploit():
    ips = set()

    def __init__(self, requester, args):
        logging.info("Module '{}' launched !".format(name))

        # concurrent requests in order to limit the time
        self.add_range("192.168.1.0/24")  # Default network 
        self.add_range("192.168.0.0/24")  # Default network 
        self.add_range("172.17.0.0/16")   # Docker network
        self.add_range("172.18.0.0/16")   # Docker network
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
            future_to_url = {executor.submit(self.concurrent_request, requester, args.param, ip, "80"): ip for ip in self.ips}


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


    def concurrent_request(self, requester, param, host, port):
        try:
            payload = wrapper_http("", host, port.strip())
            r = requester.do_request(param, payload)
        
            if not "Connection refused" in r.text:
                timer = datetime.today().time().replace(microsecond=0)
                print("\t[{}] Found host :{}".format(timer, host+ " "*40))

            timer = datetime.today().time().replace(microsecond=0)
        except Exception as e:
            pass