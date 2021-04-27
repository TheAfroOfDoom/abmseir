###
# File: worker.py
# Created: 04/26/2021
# Author: Jordan Williams (jwilliams13@umassd.edu)
# -----
# Last Modified: 04/27/2021
# Modified By: Jordan Williams
###

# Common dependencies
from distributed_common import *

# Packages
import asyncio

# Modules
import graph_handler

class Worker():
    def __init__(self):
        self.sckt = get_socket()
        self.sckt.connect(ADDR)

        self.next_pid = 0

        self.queue = []         # packets waiting to be sent
        self.sent_packets = {}  # sent packets waiting for acknowledgement
    
    def next_request(self):
        if(len(self.queue) != 0):
            # Send next request in queue
            self.send(self.queue.pop(0))

    def send(self, data: str, pid = None):
        # turn params into string if it isn't one
        if(pid is None):
            packet_id = self.next_pid
            self.next_pid = (self.next_pid + 1) % MAX_PID   # wrap next packet ID
        else:
            packet_id = pid

        # Only require an acknowledgement if this is NOT an acknowledgement itself
        if(data != 'acknowledged'):
            self.sent_packets[packet_id] = data   # add this to list of packets which need confirmation

        full_packet = generate_packet(packet_id, 'worker', data)
        self.sckt.send(full_packet)

    def acknowledge(self, pid):
        ret = None
        try:
            if(self.sent_packets.get(pid) == DISCONNECT_MESSAGE):
                ret = False

            log.info(f"ACK recv: pid:{pid} ({self.sent_packets[pid][:30]})")
            del self.sent_packets[pid]
        except Exception as e:
            log.info(f"Received acknowledgement for pid:{pid} when we we didn't need it.")
            log.error(e)

        # Next request
        self.next_request()
        return ret

    def send_acknowledgement(self, pid):
        self.send("acknowledged", pid)
        #log.info("sending acknowledgement (%s)" % packet_id)

    def receive(self):
        while(True):
            pid, packet_type, msg = receive(self.sckt)
            if(msg == 'acknowledged'):
                # Stop thread if we get a disconnect acknowledgment
                if(self.acknowledge(pid) == False):
                    break
            else:
                log.info("Received new sim request")
                self.send_acknowledgement(pid)
                self.handle_simulation_request(msg) # type: ignore

    def handle_simulation_request(self, params):
        # Run new simulation based off received params
        data = self.simulate(params).to_csv(index=False)

        log.info("Simulation complete")

        # Return simulation data to socket
        self.send(data)

    def simulate(self, params):
        # Turn params into dict from str
        params = json.loads(params)

        # Import the active graph
        g = graph_handler.import_graph()

        # New simulation object
        simulation = sim.Simulation(g)
        simulation.set_parameters(params)
        log.info(simulation.get_parameters(True))

        # Run simulation
        simulation.run()

        return(simulation.data)

def main():
    worker = Worker()

    # Add packets to request queue
    worker.queue.append("register worker")

    # Initialize receiver thread
    receiver = threading.Thread(
        target = worker.receive,
        #daemon=True
    )
    receiver.start()

    # Send max of `MAX_PID // 2` requests at once
    for _ in range(MAX_PID // 2):
        # Stop early if needed
        if(len(worker.queue) == 0):
            break
        worker.next_request()

if __name__ == '__main__':
    main()