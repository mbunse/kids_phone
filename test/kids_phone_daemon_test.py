from socket_client_server import Sock_Client
import os
client = Sock_Client('./kids_phone_socket')
data = {
    "username": os.getenv("SIP_USERNAME"),
    "password":  os.getenv("SIP_PASSWORD"),
    "realm": os.getenv("SIP_REALM"),
    "proxy": os.getenv("SIP_PROXY"),
    }
client.send({"action": "register", "data": data})