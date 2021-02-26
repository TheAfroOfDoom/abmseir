###
# File: stats.py
# Created: 02/26/2021
# Author: Jordan Williams (jwilliams13@umassd.edu)
# -----
# Last Modified: 02/26/2021
# Modified By: Jordan Williams
###

# Modules
import log_handler

# Packages
import pandas as pd

if __name__ == '__main__':
    # Initialize logging object
    log = log_handler.logging

    path = './output/data/'
    path += 'simulation_2021-02-26T110727_wattsstrogatz_n1500_k42_d3_rng0.csv'

    data = pd.read_csv(path)

    log.info('Stats on %s:' % (path))
    log.info('Means:\n%s' % (data.groupby('day').mean().iloc[[0, -1]]))
    log.info('STD\n%s' % (data.groupby('day').std().iloc[[0, -1]]))