###
# File: main.py
# Created: 12/06/2020
# Author: Jordan Williams (jwilliams13@umassd.edu)
# -----
# Last Modified: 02/07/2021
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

# Packages
import numpy as np

if __name__ == '__main__':
    # Initialize logging object
    log = log_handler.logging

    # Import the active graph
    g = graph_handler.import_graph()

    # Run simulation many times to average values
    r_0s, recovereds = [], []
    for _ in range(10):
    
        # Run simulation on current active graph
        simulation = Simulation(g)
        for _ in range(100):
            simulation.run_step()
            
        r_0 = simulation.calculate_r_0()
        recovered = simulation.data['recovered'].iloc[-1]

        r_0s.append(r_0)
        recovereds.append(recovered)
        #log.info(simulation.data)
        #log.info("R_0: %.2f" % (simulation.calculate_r_0()))

    log.info('R_0:       x = %.2f, s = %.2f' % (np.mean(r_0s), np.std(r_0s)))
    log.info('Recovered: x = %.2f, s = %.2f' % (np.mean(recovereds), np.std(recovereds)))
