import importlib

from ssrfmap.core.requester import Requester
from ssrfmap.core.handler import Handler
from importlib.machinery import SourceFileLoader
from pathlib import Path
import os
import time
import logging

class SSRF(object):
    modules   = set()
    handler   = None
    requester = None

    def __init__(self, args):

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
            handler.listen_command()
            time.sleep(5)

    def load_modules(self):
        modules = Path(Path(__file__).parent.parent, 'modules')
        for module in modules.glob('[!_]*.py'):
            module = f'ssrfmap.modules.{module.name[:-3]}'
            self.modules.add(importlib.import_module(module))

    def load_handler(self, name):
        handler_file = "{}.py".format(name)
        try:
            location = os.path.join("./handlers", handler_file)
            self.handler = SourceFileLoader(handler_file, location).load_module()
        except Exception as e:
            logging.error("Invalid no such handler: {}".format(name))
            exit(1)
