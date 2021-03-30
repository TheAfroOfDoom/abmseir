###
# File: client.py
# Created: 03/29/2021
# Author: Jordan Williams (jwilliams13@umassd.edu)
# -----
# Last Modified: 03/29/2021
# Modified By: Jordan Williams
###

# Packages
import socket

HEADER = 64
PORT = 40019
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!DISCONNECT'
SERVER = '134.88.191.15'
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    print(client.recv(2048).decode(FORMAT))

send("test pee pee pee pee pee")
input()
send("test pee pee pee pee pee1")
input()
send("test pee pee pee pee pee2")
send(DISCONNECT_MESSAGE)