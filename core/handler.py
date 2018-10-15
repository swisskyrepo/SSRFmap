import socket
import threading
import time
import logging

class Handler(threading.Thread):

    def __init__(self, port):
        threading.Thread.__init__(self)
        logging.info("Handler listening on 0.0.0.0:{}".format(port))
        self.connected = False
        self.port = int(port)

    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', self.port))

        while True:
            self.socket.listen(5)
            self.client, address = self.socket.accept()
            print("Handler> New session from {}".format( address[0] ))
            self.connected = True

            response = self.client.recv(255)
            while response != b"":
                print("\n{}\nShell > $ ".format(response.decode('utf_8', 'ignore').strip()), end='')
                response = self.client.recv(255)

    def send_command(self, cmd):
        self.client.sendall(cmd.encode())

    def kill(self):
        self.client.close()
        self.socket.close()