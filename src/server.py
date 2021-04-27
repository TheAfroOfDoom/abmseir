###
# File: server.py
# Created: 03/29/2021
# Author: Jordan Williams (jwilliams13@umassd.edu)
# -----
# Last Modified: 04/27/2021
# Modified By: Jordan Williams
###

# Common dependencies
from distributed_common import *

# Packages
import pandas as pd
from io import StringIO

class Server():
    def __init__(self):
        self.sckt = get_socket()
        self.sckt.bind(ADDR)

        self.simulation_requests = {}

        self.workers = {}

        self.next_pid = 0

        self.sent_packets = {}

    def connection_handler(self):
        while True:
            # Wait for new connection
            conn, addr = self.sckt.accept()
            thread = threading.Thread(
                target = self.handle_connection,
                args = (conn, addr),
                daemon=True
            )
            thread.start()
            log.info('[ACTIVE CONNECTIONS] %s' % (threading.active_count() - 2))

    def handle_connection(self, conn, addr):
        log.info(f'[NEW CONNECTION] {addr} connected.')

        connected = True
        while(connected):
            try:
                # Receive packet
                pid, packet_type, msg = receive(conn)

                if(pid != -1 and msg is not None):
                    if(msg == "acknowledged"):
                        old_msg = self.sent_packets[addr][pid]
                        longstr = "..." if len(old_msg) > 30 else ""
                        log.info(f"ACK recv: [{addr[0]}:{addr[1]}.{pid}] ({old_msg[:30]}{longstr})")
                        #log.info(f"ACK recv: [{addr[0]}:{addr[1]}.{pid}]")
                        pass
                    else:
                        if(msg == DISCONNECT_MESSAGE):
                            connected = False
                        else:
                            self.handle_message(packet_type, msg, addr, conn)

                        # Send acknowledgement
                        packet_acknowledgement = generate_packet(pid, 'server', 'acknowledged')
                        conn.send(packet_acknowledgement)

                        longstr = "..." if len(msg) > 30 else ""
                        log.info(f"[{addr[0]}:{addr[1]}.{pid}.{packet_type}]: {msg[:30]}{longstr}")
                else:
                    log.error("[%s:%s] Bad packet received" % (addr[0], addr[1]))

            except (ConnectionResetError or ConnectionAbortedError) as e:
                connected = False
                log.warning("[%s:%s] Connection lost" % (addr[0], addr[1]))

        conn.close()

    def handle_message(self, packet_type, msg, addr, conn):
        msg = msg.lower().strip()
        if(packet_type == 'worker'):
            # Register new worker
            if(msg == 'register worker'):
                self.workers[addr] = WorkerInfo(conn, self)
            # Handle data packet (simulation sample finished)
            else:
                worker = self.workers[addr]

                df      = worker.handle_message(msg)
                client  = worker.client
                self.handle_new_sim_data(df, client)

                # Set worker to available
                worker.active = False
                worker.client = None

            # Check to see if we can send out more jobs
            self.next_job()

        elif(packet_type == 'client'):
            self.handle_new_sim_request(conn, msg, addr)

            # Check to see if we can send out more jobs
            self.next_job()

        else:
            raise Exception("Bad packet_type received in header")

    def handle_new_sim_request(self, conn, params, addr):
        if(self.simulation_requests.get(addr)):
            raise Exception(f"Simulation request already exists for client {addr}")

        params = json.loads(params)
        self.simulation_requests[addr] = SimulationRequest(conn, params)

        # Initialize sent packets list
        self.sent_packets[addr] = {}
        
    def handle_new_sim_data(self, df, client):
        simreq = self.simulation_requests[client]

        simreq.data = simreq.data.append(df)
        simreq.samples['received'] += 1

        # Send data back to client if simulation request is complete
        if(simreq.samples['received'] == simreq.samples['required']):
            packet_id = self.next_pid
            self.next_pid = (self.next_pid + 1) % MAX_PID   # wrap next packet ID

            data = simreq.data.to_csv(index=False)

            # Initialize sent packets list if necessary
            if(self.sent_packets.get(client) is None):
                self.sent_packets[client] = {}
            self.sent_packets[client][packet_id] = data
            
            data = generate_packet(packet_id, 'server', data)
            simreq.conn.send(data)

            # Remove simulation request from list
            del self.simulation_requests[client]

            # Remove this client from sent_packets list
            #del self.sent_packets[client]
    
    def next_job(self):
        # Check if we have any inactive workers
        inactive_workers = [(addr, worker) for (addr, worker) in self.workers.items() if not worker.active] # type: list[tuple]

        # Check if we have any simulation requests that need runs
        simreqs = [(addr, simreq) for (addr, simreq) in self.simulation_requests.items() if simreq.samples['requested'] < simreq.samples['required']]

        # Distribute jobs
        while(len(inactive_workers) > 0 and len(self.simulation_requests) > 0):
            client, simreq = simreqs.pop(0)

            while(len(inactive_workers) > 0 and simreq.samples['requested'] < simreq.samples['required']):
                addr, next_worker = inactive_workers.pop(0)

                # Give the next worker a job
                next_worker.start(json.dumps(simreq.params), client)
                simreq.samples['requested'] += 1

    def start(self):
        self.sckt.listen()
        log.info('[LISTENING] Server is listening on %s:%s' % (SERVER, PORT))

        # Create connection handler thread
        thread = threading.Thread(target=self.connection_handler, daemon=True)
        thread.start()

        # Listen for server admin input
        while True:
            command = input()
            if(command == SERVER_QUIT_MESSAGE):
                break

class SimulationRequest():
    def __init__(self, conn, params):
        for key in params.keys():
            self.__setattr__(key, params[key])

        self.data = pd.DataFrame(dtype = int)

        self.samples['received'] = self.samples['requested'] = 0    # type: ignore

        self.conn = conn

class WorkerInfo():
    def __init__(self, conn, server):
        self.active = False
        self.client = None
        self.conn = conn;
        self.connected = True;
        self.server = server

        self.next_pid = 0

    def start(self, params, client, pid = None):
        self.active = True
        self.client = client

        addr = self.conn.getpeername()

        if(pid is None):
            packet_id = self.next_pid
            self.next_pid = (self.next_pid + 1) % MAX_PID   # wrap next packet ID
        else:
            packet_id = pid

        # Initialize sent packets list if necessary
        sent_packets = self.server.sent_packets
        if(sent_packets.get(addr) is None):
            sent_packets[addr] = {}
        sent_packets[addr][packet_id] = params   # add this to list of packets which need confirmation

        simulation_request = generate_packet(packet_id, 'server', params)
        self.conn.send(simulation_request)
    
    def handle_message(self, msg):
        # try to save msg to dataframe
        df = pd.read_csv(StringIO(msg))

        return(df)

if __name__ == '__main__':
    log.info('[STARTING] Server is starting...')
    server = Server()
    server.start()
