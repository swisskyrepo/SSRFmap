import importlib
import logging
import os
import time
from importlib.machinery import SourceFileLoader
from pathlib import Path

from ssrfmap.core.config import SsrfmapConfig
from ssrfmap.core.handler import Handler
from ssrfmap.core.requester import Requester


class SSRF(object):
    modules: set[object] = set()

    def __init__(self, config: SsrfmapConfig):

        # Load modules in memory
        self.load_modules()

        # Start a reverse shell handler
        if config.handler and config.lport and config.handler == "1":
            handler = Handler(config.lport)
            handler.start()
        elif config.handler and config.lport:
            self.load_handler(config.handler)
            handler = self.handler.exploit(config.lport)
            handler.start()

        # Init a requester
        self.requester = Requester(config.reqfile, config.useragent, config.ssl)

        if config.param is None:
            logging.warning("No parameter (-p) defined, nothing will be tested!")

        if config.modules is None:
            logging.warning("No modules (-m) defined, everything will be tested!")
            for module in self.modules:
                module.exploit(self.requester, config)
        else:
            for m in self.modules:
                if m.name in config.modules:  # type: ignore
                    m.exploit(self.requester, config)  # type: ignore

        # Handling a shell
        while config.handler:
            handler.listen_command()
            time.sleep(5)

    def load_modules(self):
        modules = Path(Path(__file__).parent.parent, "modules")
        for module in modules.glob("[!_]*.py"):
            module = f"ssrfmap.modules.{module.name[:-3]}"
            self.modules.add(importlib.import_module(module))

    def load_handler(self, name):
        handler_file = "{}.py".format(name)
        try:
            location = os.path.join("./handlers", handler_file)
            self.handler = SourceFileLoader(handler_file, location).load_module()
        except Exception as e:
            logging.error("Invalid no such handler: {}".format(name))
            exit(1)
