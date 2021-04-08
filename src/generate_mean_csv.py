###
# File: generate_mean_csv.py
# Created: 03/30/2021
# Author: Jordan Williams (jwilliams13@umassd.edu)
# -----
# Last Modified: 04/07/2021
# Modified By: Jordan Williams
###

# type: ignore

import glob
import os
import pandas as pd
import numpy as np

if __name__ == '__main__':
    path = './output/data/'
    files = [
        'simulation_2021-04-07T173927_complete_n1000.csv',
       'latest'
    ]

    list_of_files = glob.glob(path + '*.csv')
    latest_file = max(list_of_files, key=os.path.getctime)
    latest_file = latest_file[latest_file.rfind('\\'):]
    files = [latest_file if f == 'latest' else f for f in files]

    data = pd.concat((pd.read_csv(path + f, comment = '#') for f in files))

    dgbd = data.groupby('cycle')

    total = data.iloc[0].sum()
    dfmean = dgbd.mean()

    cols = ['susceptible', 'exposed',
            'infected asymptomatic', 'infected symptomatic',
            'recovered', 'deceased', 'test count',
            'true positive', 'false positive',
            'new false positive', 'returning false positive'
        ,   'exogenous', 'generation 1', 'generation 2', 'generation 3'
        , 'generation 4', 'generation 5', 'generation x']
    dfmean[cols].to_csv('%s/mean/%s' % (path, files[0]))

#'''