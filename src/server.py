###
# File: server.py
# Created: 03/29/2021
# Author: Jordan Williams (jwilliams13@umassd.edu)
# -----
# Last Modified: 03/29/2021
# Modified By: Jordan Williams
###

# Packages
import socket
import threading

HEADER = 64
PORT = 40019
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!DISCONNECT'
SERVER_QUIT_MESSAGE = '!QUIT'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def handle_client(conn, addr):
    print(f'[NEW CONNECTION] {addr} connected.')

    connected = True
    while(connected):
        # Determine msg length from header
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if(msg_length):
            msg_length = int(msg_length)

            msg = conn.recv(msg_length).decode(FORMAT)
            if(msg == DISCONNECT_MESSAGE):
                connected = False

            print("[%s] %s" % (addr, msg))

            conn.send("message received".encode(FORMAT))

    conn.close()

def start():
    server.listen()
    print('[LISTENING] Server is listening on %s:%s' % (SERVER, PORT))

    # Create connection handler thread
    thread = threading.Thread(target=connection_handler, daemon=True)
    thread.start()

    # Listen for server admin input
    while True:
        command = input()
        if(command == SERVER_QUIT_MESSAGE):
            break


def connection_handler():
    while True:
        # Wait for new connection
        conn, addr = server.accept()
        thread = threading.Thread(
            target = handle_client,
            args = (conn, addr),
            daemon=True
        )
        thread.start()
        print('[ACTIVE CONNECTIONS] %s' % (threading.active_count() - 2))


print('[STARTING] Server is starting...')
start()