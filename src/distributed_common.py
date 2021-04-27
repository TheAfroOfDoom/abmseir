###
# File: distributed_common.py
# Created: 04/26/2021
# Author: Jordan Williams (jwilliams13@umassd.edu)
# -----
# Last Modified: 04/26/2021
# Modified By: Jordan Williams
###

# Packages
import json
import socket
import threading

# Modules
import simulation as sim
import log_handler

HEADER_LENGTH = 128
MAX_PID = 1024
TIMEOUT_TIME = 2000 # ms

PORT = 40019
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!DISCONNECT'
SERVER_QUIT_MESSAGE = '!QUIT'

def get_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def generate_packet(pid, packet_type, msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)

    header = (f'pid:{pid},{packet_type},{str(msg_length)}').encode(FORMAT)
    header += b' ' * (HEADER_LENGTH - len(header))
    header = header.decode(FORMAT)

    packet = (header + msg).encode(FORMAT)
    return packet

def receive(conn):
    # Determine msg length from header
    header = conn.recv(HEADER_LENGTH).decode(FORMAT)
    
    '''
    # ignore blank packets (why is this not the default???)
    if(len(header == 0)):
        return(-1, None, None)
    '''

    pid, packet_type, packet_length = header.split(',')

    if(pid and packet_type and packet_length):
        pid, packet_length = int(pid.split(":")[1]), int(packet_length)

        msg = conn.recv(packet_length).decode(FORMAT)
        return(pid, packet_type, msg)

    else:
        return(-1, None, None)

log = log_handler.logging