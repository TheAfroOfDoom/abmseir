###
# File: main.py
# Created: 12/06/2020
# Author: Jordan Williams (jwilliams13@umassd.edu)
# -----
# Last Modified: 01/26/2021
# Modified By: Jordan Williams
###

# MTH 465 - Small World Networks
# Final Project - Post-semester revisions
# made in Python 3.9.0

"""
Modelling the Spread of SARS-CoV-2 at UMass Dartmouth using Small World Networks
"""

# Modules
import config
import log_handler
import graph_handler

# Packages
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import os
import pandas as pd
import random
import re
import seaborn as sns
import sys

# Initialize logging object
log = log_handler.logging

# Import active graph defined in config
g = graph_handler.import_graph()

### PUSH just to get some updated code to git (not fully modular yet)
'''
# Graph config settings
active_graph_count = config.settings['graph']['active']['count']

graph_directory = config.settings['graph']['directory']
graph_extension = config.settings['graph']['extension']
graph_file_name_pattern = graph_handler.build_file_name().replace(graph_extension, '[\w]*%s' % (graph_extension))

# Prepare list of active graphs to iterate through
active_graph_files = [f for f in os.listdir('./' + graph_directory)
                        if re.match(r'^%s$' % (graph_file_name_pattern), f)]
'''

'''
# TODO(jordan): Need to bring this into `graph_handler.py` and make it grab the required number of graphs specified in config, and generate more if there aren't enough.
active_graphs = []

for i in range(active_graph_count):

# Iterate through the active graphs
for g in active_graphs:

    # Import the active graph
    g = graph_handler.import_graph()

    # Run simulation on current active graph
'''

SAMPLE_SIZE = 50

def makeGraphs(testRates, caseTypes):
    fig, axs = plt.subplots(nrows = len(testRates), ncols = len(caseTypes))
    # Each row is a test rate (least-often to most-often)
    for i, testRate in enumerate(reversed(testRates)):
        if(len(caseTypes) > 1):
            # Each column is a case (best, base, worst)
            for j, caseType in enumerate(caseTypes):
                ax = axs[i, j]

                rt = caseType[0]
                X = caseType[1]

                # infection rate
                ir = BASE_INFECTION_RATE[rt]

                simulationContainer(ax, testRate, rt, X, SAMPLE_SIZE)
        else:
            ax = axs[i]

            rt = caseTypes[0][0]
            X = caseTypes[0][1]

            # infection rate
            ir = BASE_INFECTION_RATE[rt]

            simulationContainer(ax, testRate, rt, X, SAMPLE_SIZE)

    xlab = 'Days'
    ylab = 'Cases'
    for ax in axs.reshape(-1):
        ax.set(xlabel = xlab, ylabel = ylab)
        ax.label_outer()

    l = ["Infected", "Recovered", "Susceptible"]
    if(len(caseTypes) > 1):
        axs[0, -1].legend(l)
    else:
        axs[0].legend(l)

    colLabels = [r"%s Graph: $\beta$: %.2f%%, X: %d" % (conf.config['graph']['type'], 100 * BASE_INFECTION_RATE[caseType[0]], caseType[1]) for caseType in caseTypes]
    rowLabels = ["%d days" % (testRate) if isinstance(testRate, int) else testRate for testRate in reversed(testRates)]

    # Fancy column/row labels in addition to subplot labels
    # https://stackoverflow.com/a/25814386/13789724
    pad = 5 # in points

    '''
    for ax, col in zip(axs[0], colLabels):
        ax.annotate(col, xy=(0.5, 1), xytext=(0, pad),
                    xycoords=ax.title, textcoords='offset points',
                    size='large', ha='center', va='baseline')
    '''
    fig.suptitle(colLabels[0])

    for ax, row in zip(axs, rowLabels):
        ax.annotate(row, xy=(0, 0.5), xytext=(-ax.yaxis.labelpad - pad, 0),
                    xycoords=ax.yaxis.label, textcoords='offset points',
                    size='large', ha='right', va='center')

    fig.tight_layout()
    # tight_layout doesn't take these labels into account. We'll need 
    # to make some room. These numbers are are manually tweaked. 
    # You could automatically calculate them, but it's a pain.
    #fig.subplots_adjust(left=0.15, top=0.95)
    fig.subplots_adjust(left=0.4)
    #fig.set_size_inches()

    plt.show()

# test cases to see if output is correct
#testRates = [7, "None"]
#castTypes = [CASE_TYPES[0], CASE_TYPES[1]]
#SAMPLE_SIZE = 1

#caseTypes = CASE_TYPES      # cols
'''
testRates = [TEST_RATES[-1], TEST_RATES[-2]]
for caseTypes in CASE_TYPES[2:]:
    makeGraphs(testRates, [caseTypes])
'''
#'''
testRates = TEST_RATES[3:]  # split rows in half
for caseTypes in CASE_TYPES:
    makeGraphs(testRates, [caseTypes])
#'''
testRates = TEST_RATES[:3]  # split rows in half
for caseTypes in CASE_TYPES:
    makeGraphs(testRates, [caseTypes])
#'''
