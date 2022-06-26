###
# File: generate_mean_csv.py
# Created: 03/30/2021
# Author: Jordan Williams (theafroofdoom@gmail.com)
# -----
# Last Modified: 06/04/2022
# Modified By: Jordan Williams
###

# type: ignore

import glob
import os
import pandas as pd
import numpy as np

if __name__ == "__main__":
    path = "./output/data/"
    files = [
        #'simulation_2021-04-08T200447_complete_n1000.csv',
        #'simulation_2021-04-08T202647_complete_n1000.csv',
        "latest"
    ]

    list_of_files = glob.glob(path + "*.csv")
    latest_file = max(list_of_files, key=os.path.getctime)
    latest_file = latest_file[latest_file.rfind("\\") :]
    files = [latest_file if f == "latest" else f for f in files]

    data = pd.concat((pd.read_csv(path + f, comment="#") for f in files))

    data["interactions*"] = data["susceptibles contracting"] * data["infected nodes"]
    dgbd = data.groupby("cycle")

    dfmean = dgbd.mean()

    cols = [
        "susceptible",
        "exposed",
        "infected asymptomatic",
        "infected symptomatic",
        "recovered",
        "deceased",
        "test count",
        "true positive",
        "false positive",
        "new false positive",
        "returning false positive",
        "exogenous",
        "generation 1",
        "generation 2",
        "generation 3",
        "generation 4",
        "generation 5",
        "generation x",
        "interactions",
        "infected nodes",
        "susceptibles contracting",
        "interactions*",
    ]
    dfmean[cols].to_csv("%s/mean/%s" % (path, files[0]))

#'''
