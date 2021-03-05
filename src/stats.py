###
# File: stats.py
# Created: 02/26/2021
# Author: Jordan Williams (jwilliams13@umassd.edu)
# -----
# Last Modified: 03/03/2021
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
    path += 'simulation_2021-03-03T150522_complete_n1500.csv'

    data = pd.read_csv(path, comment = '#')

    log.info('Stats on %s:' % (path))
    log.info('Means:\n%s'   % (data.groupby('day').mean().iloc[-1]))
    log.info('STD\n%s'      % (data.groupby('day').std().iloc[-1]))