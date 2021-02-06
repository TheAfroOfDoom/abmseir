###
# File: main.py
# Created: 12/06/2020
# Author: Jordan Williams (jwilliams13@umassd.edu)
# -----
# Last Modified: 02/06/2021
# Modified By: Jordan Williams
###

# MTH 465 - Small World Networks
# Final Project - Post-semester revisions
# made in Python 3.9.0

"""
Modelling the Spread of SARS-CoV-2 at UMass Dartmouth using Small World Networks
"""

# Modules
import log_handler
import graph_handler
from simulation import Simulation

if __name__ == '__main__':
    # Initialize logging object
    log = log_handler.logging

    # Import the active graph
    g = graph_handler.import_graph()

    # Run simulation on current active graph
    simulation = Simulation(g)
    for _ in range(100):
        simulation.run_step()
    log.info(simulation.data)
    log.info("R_0: %.2f" % (simulation.calculate_r_0()))