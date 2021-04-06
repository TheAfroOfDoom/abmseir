###
# File: stats.py
# Created: 02/26/2021
# Author: Jordan Williams (jwilliams13@umassd.edu)
# -----
# Last Modified: 04/05/2021
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
    path += 'simulation_2021-02-28T190137_complete_n1500.csv'

    data = pd.read_csv(path, comment = '#')

    dgbd = data.groupby('cycle')
    log.info('\nStats on %s:' % (path))
    log.info('\nMean S: %s' % (dgbd.mean().get('susceptible').iloc[-1]))
    log.info('STD: %s' % (dgbd.std().get('susceptible').iloc[-1]))
    
    paltiel = 816
    total = data.iloc[0].sum()
    total_infected = total - dgbd.mean().get('susceptible').iloc[-1]
    #error = (total_infected - paltiel) / paltiel
    log.info('Samples: %d' % (dgbd.count().get('susceptible').iloc[-1]))
    log.info(total_infected)#, '(%.4f%%)' % (error * 100))