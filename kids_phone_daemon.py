#!/usr/bin/python

import os
import logging
import threading
import socket
import struct
import signal

from socket_client_server import Sock_Server
from kids_phone import Kids_Phone

class Kids_Phone_Daemon():
    def __init__(self):
        server_address = os.getenv("KIDS_PHONE_SOCKET", './kids_phone_socket')
        
        self.sock_server = Sock_Server(server_address, self.request_handler)
        self.kids_phone = Kids_Phone()
        self.__kids_phone_thread = threading.Thread(target=self.kids_phone.run)
        self.__kids_phone_thread.start()
        self.sock_server.start()
        signal.signal(signal.SIGINT, self.signal_handler)

    def request_handler(self, data):
        try:
            if data["action"] == "register":
                username = data["data"]["username"]
                password = data["data"]["password"]
                realm = data["data"]["realm"]
                self.kids_phone.register(username, password, realm)
        except KeyError:
            logging.error("unexpected key in message")
        return None
    def signal_handler(self, signal, frame):
        self.quit()

    def quit(self):
        self.sock_server.quit()
        self.kids_phone.quit = True
        self.__kids_phone_thread.join()
        return

if __name__ == "__main__":
    import time
    from socket_client_server import Sock_Client

    daemon = Kids_Phone_Daemon()
    time.sleep(1)
    client = Sock_Client(daemon.sock_server.server_address)
    client.send({"action": "register", "data": {"username": "username", "password": "password", "realm": "realm"}})
    daemon.quit()


