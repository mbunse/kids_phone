#!/usr/bin/python

import logging
import threading
import socket
import struct
import json
import os

class Sock_Base:
    def __init__(self, server_address):
        self.server_address = server_address
    def send_msg(self, connection, data):
        # serialize as JSON
        msg = json.dumps(data)
        # Prefix each message with a 4-byte length (network byte order)
        msg = struct.pack('>I', len(msg)) + msg
        connection.sendall(msg)
        return

    def recv_msg(self, connection):
        # Read message length and unpack it into an integer
        raw_msglen = self.recvall(connection, 4, decode_json=False)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        # Read the message data
        return self.recvall(connection, msglen)

    def recvall(self, connection, n, decode_json=True):
        # Helper function to recv n bytes or return None if EOF is hit
        data = b''
        while len(data) < n:
            packet = connection.recv(n - len(data))
            if not packet:
                return None
            data += packet
        # deserialize JSON
        if decode_json:
            data = json.loads(data)
        return data

class Sock_Client(Sock_Base):
    def send(self, data):
        try:
            logging.info("Client conntecting to {server}".format(server=self.server_address))
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.server_address)
        except socket.error, msg:
            logging.error("Client cannot conntect to {server}: {msg}".format(server=self.server_address, msg=msg))
            return None
        self.send_msg(sock, data)
        answer = self.recv_msg(sock)
        sock.close()
        return answer



class Sock_Server(Sock_Base, threading.Thread):
    def __init__(self, server_address, request_handler):
        """
        Parameters
        ==========
        server_address:  socket address

        request_handler: function with one string parameter for
            incoming message returning return message or None
        """
        # Make sure the socket does not already exist
        threading.Thread.__init__(self)

        try:
            os.unlink(server_address)
        except OSError:
            if os.path.exists(server_address):
                raise

        Sock_Base.__init__(self, server_address)
        self.request_handler = request_handler
        self.__quit = threading.Event()
    def quit(self):
        if self.__quit is not None:
            self.__quit.set()
        self.join()
        return

    def run(self):
        # Bind the socket to the port
        logging.info("Server starts socket on {addr}".format(addr=self.server_address))

        # Create a UDS socket
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.bind(self.server_address)
        # set timeout for accept to 2 seconds
        self.sock.settimeout(2)
        # Listen for incoming connections
        self.sock.listen(1)
        while not self.__quit.is_set():
            # Wait for incoming connections
            logging.info("Server waits for connections")
            try:
                connection, client_address = self.sock.accept()
            except socket.timeout:
                continue
            logging.info("Server received connection from {addr}".format(addr=client_address))
            data = self.recv_msg(connection)
            answer = self.request_handler(data)
            if answer is not None:
                self.send_msg(connection, answer)
            connection.close()
        self.sock.close()
        try:
            os.unlink(self.server_address)
        except OSError:
            if os.path.exists(self.server_address):
                raise
        return
        
if __name__ == "__main__":

    import time
    logging.basicConfig(level=logging.DEBUG)

    def request_handler(data):
        return data

    logging.info("starting server")
    server = Sock_Server("test_socket", request_handler)
    logging.info("listening")
    server.start()
    time.sleep(1)
    client = Sock_Client("test_socket")
    print client.send({"test": 0, "msg": "Hallo Welt!"})
    server.quit()


