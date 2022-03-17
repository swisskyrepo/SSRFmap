from core.utils import *
from core.handler import Handler
import re
import logging
import urllib.parse

class exploit(Handler):

  def __init__(self, port):
    super().__init__(port)

  def run(self):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.socket.bind(('', self.port))
    self.injected_params = []

    while True:
        self.socket.listen(5)
        self.client, address = self.socket.accept()

        response = self.client.recv(1024).decode()
        if self.socket._closed or not response:
            break

        logging.info(f"New session from : \033[32m{address[0]}\033[0m")
        self.connected = True

        regex = re.compile('(.*) (.*) HTTP')
        request_method, request_action = regex.findall(response)[0]
        request_param = urllib.parse.urlsplit(request_action).query
        logging.info(f"Possible injected param: \033[32m{request_param}\033[0m")
        self.injected_params.append(request_param)

        response_header = "HTTP/1.1 200 OK\n"
        response_header += 'Server: I-See-You\n'
        response_header += 'Connection: close\n\n'
        self.client.send(response_header.encode())
        self.client.close()

  def kill(self):
    socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(self.socket.getsockname()) # trigger last connection to closing
    self.socket.close()

  def listen_command(self):
    # shutdown handler
    if not self.socket._closed:
      self.kill()
    else:
      exit()
