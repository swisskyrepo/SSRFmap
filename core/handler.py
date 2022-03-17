import socket
import threading
import time
import logging

class Handler(threading.Thread):

    def __init__(self, port):
        threading.Thread.__init__(self)
        logging.info(f"Handler listening on 0.0.0.0:{port}")
        self.connected = False
        self.port = int(port)

    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', self.port))

        while True:
            self.socket.listen(5)
            self.client, address = self.socket.accept()
            print(f"Handler> New session from {address[0]}")
            self.connected = True

            response = self.client.recv(255)
            while response != b"":
                print(f"\n{response.decode('utf_8', 'ignore').strip()}\nShell > $ ", end='')
                response = self.client.recv(255)

    def listen_command(self):
        if self.connected == True:
            cmd = input("Shell> $ ")
            if cmd == "exit":
                self.kill()
                print("BYE !")
                exit()
                self.send_command(cmd+"\n\n")

    def send_command(self, cmd):
        self.client.sendall(cmd.encode())

    def kill(self):
        self.client.close()
        self.socket.close()