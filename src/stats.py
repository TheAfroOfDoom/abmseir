###
# File: stats.py
# Created: 02/26/2021
# Author: Jordan Williams (jwilliams13@umassd.edu)
# -----
# Last Modified: 04/06/2021
# Modified By: Jordan Williams
###

import pandas as pd

if __name__ == '__main__':
    path = './output/data/'
    file = 'simulation_2021-04-06T171437_complete_n1000.csv'

    data = pd.read_csv(path + file, comment = '#')

    dgbd = data.groupby('cycle')
    print('\nStats on %s:' % (path + file))
    
    paltiel = 351
    tests = 4881
    total = data.iloc[0].sum()
    total -= data.get('test count').iloc[0]
    total -= data.get('true positive').iloc[0]
    total -= data.get('false positive').iloc[0]

    test_count = dgbd.mean().get('test count').iloc[-1]

    total_infected = total - dgbd.mean().get('susceptible').iloc[-1]
    error = (total_infected - paltiel) / paltiel
    error_tests = (test_count - tests) / tests
    
    print('TI: ', total_infected, '(err: %.4f%%)' % (error * 100))
    print('Tests: %s (err: %.4f%%)' % (test_count
                                , (error_tests * 100)))
    print('Samples: %d\n' % (dgbd.count().get('susceptible').iloc[-1]))

    for column in ['susceptible', 'false positive', 'infected asymptomatic', 'true positive', 'infected symptomatic', 'recovered', 'deceased']:
        print(f'{column}: %s (%s)' % (dgbd.mean().get(column).iloc[-1]
                                , dgbd.std().get(column).iloc[-1]))