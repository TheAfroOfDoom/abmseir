###
# File: main.py
# Created: 12/06/2020
# Author: Jordan Williams (jwilliams13@umassd.edu)
# -----
# Last Modified: 03/03/2021
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
import datetime
import numpy as np
import pandas as pd
import pprint

if __name__ == '__main__':
    # Initialize logging object
    log = log_handler.logging

    # Import the active graph
    g = graph_handler.import_graph()

    # Run simulation on current active graph
    simulation = Simulation(g)
    time = datetime.datetime.now().strftime('%Y-%m-%dT%H%M%S')
    default_extension = '.csv'
    path = './output/data/simulation_%s_%s' % (time, simulation.graph.name + default_extension)

    # Write simulation params to header comment
    pp = pprint.PrettyPrinter(indent = 4)
    file = open(path, 'a')
    file.write('# %s\n' % ('\n# '.join((pp.pformat(simulation.get_parameters(all = True)) + '\n\n').split('\n'))))
    file.close()

    # Write simulation columns to header
    simulation.data.to_csv(path, mode = 'a')

    # Run simulation many times to average values
    r0s, total_infecteds = [], []
    simulation_params = None

    # NOTE(jordan): SAMPLE SIZE IS HERE
    sample_size = 1
    for i in range(sample_size):
        # Run simulation on current active graph
        simulation = Simulation(g)

        # Track params
        sp = simulation.get_parameters(all = True)
        if(simulation_params != sp):
            simulation_params = sp
            log.info('Simulation-%d parameters at t = %d:\n%s' % (i, simulation.time, pp.pformat(simulation_params)))

        # Run simulation
        simulation.run()
            
        r0 = simulation.calculate_r0()
        susceptible = simulation.data['susceptible'].iloc[-1]

        r0s.append(r0)
        total_infecteds.append(len(g) - susceptible)

        # Append to file
        simulation.data.to_csv(path, mode = 'a', header = False)

    log.info("Saved simulation data from %d samples to '%s'" % (sample_size, path))

    log.info('R0:              x = %.2f, s = %.2f' % (np.mean(r0s), np.std(r0s)))
    log.info('Total Infected:   x = %.2f, s = %.2f' % (np.mean(total_infecteds), np.std(total_infecteds)))
#    log.info('R0s:      %s' % (r0s))