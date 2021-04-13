###
# File: stats.py
# Created: 03/05/2021
# Author: Jordan Williams (jwilliams13@umassd.edu)
# -----
# Last Modified: 04/09/2021
# Modified By: Jordan Williams
###

# type: ignore

import glob
import os
import pandas as pd

if __name__ == '__main__':
    path = './output/data/'
    files = [
        #'simulation_2021-04-08T200447_complete_n1000.csv',
        #'simulation_2021-04-09T105832_complete_n1000.csv'
        'latest'
    ]

    list_of_files = glob.glob(path + '*.csv')
    latest_file = max(list_of_files, key=os.path.getctime)
    latest_file = latest_file[latest_file.rfind('\\'):].replace("\\", "")
    files = [latest_file if f == 'latest' else f for f in files]

    data = pd.concat((pd.read_csv(path + f, comment = '#') for f in files))

    f1 = data['cycle'] == 239
    data['interactions*'] = data['susceptibles contracting']*data['infected nodes']
    f2 =  data['interactions*'] != data['interactions']

    #data = data.where(f1)# & f2)
    #data = data[data.cycle == 239]


    data[['cycle', 'susceptible', 'infected asymptomatic', 'interactions', 'interactions*']].to_csv('%s/test/%s' % (path, files[0]))

    #dgbd = data.groupby('cycle')
    print('\nStats on %s:' % (files))
    
    paltiel = 188
    tests = 0

'''
    population_cols = ['susceptible', 'exposed', 'infected asymptomatic', 'infected symptomatic',
        'recovered', 'deceased']
    total = data[population_cols].iloc[0].sum()

    dgbgm = dgbd.mean()

    test_count = dgbgm.get('test count').iloc[-1]


    total_infected = total - dgbgm.get('susceptible').iloc[-1]
    error = (total_infected - paltiel) / paltiel
    error_tests = test_count if tests == 0 else (test_count - tests) / tests
    
    print('TI: ', total_infected, '(err: %.4f%%)' % (error * 100))
    print('Tests: %s (err: %.4f%%)' % (test_count
                                , (error_tests * 100)))
    print('Samples: %d\n' % (dgbd.count().get('susceptible').iloc[-1]))

    for column in ['susceptible', 'false positive', 'infected asymptomatic', 'true positive', 'infected symptomatic', 'recovered', 'deceased']:
        print(f'{column}: %s (%s)' % (dgbgm.get(column).iloc[-1]
                                , dgbd.std().get(column).iloc[-1]))

    cols = ['generation 1', 'generation 2', 'generation 3', 'generation 4']
    dgens = dgbgm[cols].iloc[-1]
    r0 = dgens.get('generation 2') / dgens.get('generation 1')
    r1 = dgens.get('generation 3') / dgens.get('generation 2')
    r2 = dgens.get('generation 4') / dgens.get('generation 3')

    print(f'R0: {r0} \nR1: {r1} \nR2: {r2}')
'''