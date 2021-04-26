###
# File: main.py
# Created: 12/06/2020
# Author: Jordan Williams (jwilliams13@umassd.edu)
# -----
# Last Modified: 04/15/2021
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
    rs, total_infecteds = [[], [], []], []
    simulation_params = None
    t0 = t1 = None

    # NOTE(jordan): SAMPLE SIZE IS HERE
    sample_size = 200
    for i in range(sample_size):
        # Run simulation on current active graph
        simulation = Simulation(g)

        # Track params
        sp = simulation.get_parameters(all = True)
        if(simulation_params != sp):
            simulation_params = sp
            log.info('Simulation-%d parameters at t = %d:\n%s' % (i, simulation.time_index, pp.pformat(simulation_params)))

        # Run simulation
        simulation.run()

        gens = simulation.calculate_r0()
        gen1 = gens.get('generation 1')
        gen2 = gens.get('generation 2')
        gen3 = gens.get('generation 3')
        gen4 = gens.get('generation 4')
        gen5 = gens.get('generation 5')

        r0 = 0 if gen1 == 0 else gen2 / gen1    # type: ignore
        r1 = 0 if gen2 == 0 else gen3 / gen2    # type: ignore
        r2 = 0 if gen3 == 0 else gen4 / gen3    # type: ignore
        susceptible = simulation.data['susceptible'].iloc[-1]

        rs[0].append(r0)
        rs[1].append(r1)
        rs[2].append(r2)
        total_infecteds.append(len(g) - susceptible)    # type: ignore

        # Append to file
        simulation.data.to_csv(path, mode = 'a', header = False)

        # Save start time
        if(t0 is None):
            t0 = simulation.time[0]

    # Save final time
    t1 = simulation.time[1]
    td = t1 - t0    # type: ignore

    log.info("Saved simulation data from %d samples to '%s' | %.2fs runtime (%.4fs each)" % (sample_size, path,
        td.total_seconds(), td.total_seconds() / sample_size))
    log.info('R0:               x = %.2f, s = %.2f' % (np.mean(rs[0]), np.std(rs[0])))
    log.info('R1:               x = %.2f, s = %.2f' % (np.mean(rs[1]), np.std(rs[1])))
    log.info('R2:               x = %.2f, s = %.2f' % (np.mean(rs[2]), np.std(rs[2])))
    log.info('Total Infected:   x = %.2f, s = %.2f' % (np.mean(total_infecteds), np.std(total_infecteds)))