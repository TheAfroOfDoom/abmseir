###
# File: simulation.py
# Created: 01/25/2021
# Author: Jordan Williams (jwilliams13@umassd.edu)
# -----
# Last Modified: 01/29/2021
# Modified By: Jordan Williams
###

"""
Simulates the infectious spread across a community (graph) based on parameters defined in config.json.
"""

# Modules
import config
from log_handler import logging as log

# Packages
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import os
import pandas as pd
import random
import seaborn as sns
import sys

def bisect(lo, hi):
    '''Returns the average of two numeric parameters.
    '''
    return (lo + hi) / 2

def calculate_infection_rate(graph, node_degree, desired_rt, error):
    '''Calculates the infection rate for a desired `Rt` value
    through what is essentially trial and error w/binary search:
    1. Run the simulation until all Gen.1 infections recover
    2. Compare measured R_t to desired R_t
    3. Use binary search to update bounds
    4. Repeat
    '''
    # Initial bounds
    lower_bound = 0
    upper_bound = node_degree

    while(True):
        # Update guess
        infection_rate = bisect(lower_bound, upper_bound)

        # Run simulation TODO(jordan): <until all Gen.1 infections recover and save measured Rt>
        # TODO(jordan): Get the average `measured_rt` of multiple simulations.
        measured_rt = run_simulation()

        # Update bounds
        if(measured_rt > desired_rt + error):
            upper_bound = infection_rate
        elif(measured_rt < desired_rt - error):
            lower_bound = infection_rate
        # Break when we measure an rt within the error of our desired_rt
        else:
            break

    return(infection_rate)

def geometric_by_mean(rng, mean):
    # https://en.wikipedia.org/wiki/Geometric_distribution (mean = 1 / p)
    p = 1 / (mean)

    return(rng.geometric(p))

class Test:
    '''Handles everything related to a node's testing:
    1. How many tests it has taken
    2. The results of its last test
    3. If it is waiting on test results
        - If so, how long it has been waiting
    '''
    def __init__(self, rng, node):
        # Numpy random number generator object
        self.rng = rng

        # Associated node
        self.node = node

        # Number of tests this node has taken
        self.count = 0

        # True means the test indicated infection in the individual
        self.results = True

        # Time this node needs to wait until it gets its test results
        self.delay = 0
        self.processing_results = False

    def update(self, global_time, test_settings, time_to_recovery):
        '''Runs once per cycle per node, updating its test information as follows:
        1. Waits for the test result's delay
            - Updates its node based on the results
        2. 
        '''
        test_rate = test_settings['test_rate']

        # If we are waiting on the latest test results, decrement the delay we are waiting
        if(self.processing_results):
            self.delay -= 1

        # Determine if we should get tested                         # Only test if:
        bool_should_get_tested  =   isinstance(test_rate, int)      #       `test_rate` is numerical
        bool_should_get_tested &=   test_rate != 0                  # and   if `test_rate` is not 0
        bool_should_get_tested &=   global_time % test_rate == 0    # and   if the current `global_time` is
                                                                    #       divisible by our `test_rate`

        bool_should_get_tested |=   (test_rate == 'symptom-based'   # or    if we are testing based on symptoms,
                                    and self.node.symptoms)         #       and our node is symptomatic

        bool_should_get_tested &=   global_time > 0                 # and   if this isn't the first day of the simulation
        bool_should_get_tested &=   self.node.quarantine_time == 0  # and   if we aren't in quarantine

        # Get tested if the above conditions pass
        if(bool_should_get_tested):
            self.take(test_settings)

        # Receive test results Y days after being tested (if not quarantined)
        if(self.processing_results
        and self.delay == 0):
            self.get_test_results(time_to_recovery)

    def take(self, test_settings):
        '''Simulates a node taking a COVID test.
        Returns a boolean based on sensitivity/specificity parameters
        and whether or not the node is actually infected or not.
        '''
        sensitivity = test_settings['sensitivity']
        specificity = test_settings['specificity']
        test_results_delay = test_settings['test_results_delay']

        # Increment the amount of tests this node has taken
        self.count += 1

        # Use positive rates for infected individuals
        if(self.state == 'infected asymptomatic'
        or self.state == 'infected symptomatic'):
            if(self.rng.random() <= sensitivity):
                self.results = True
            else:
                self.results = False
                pass

        # Use negative rates for susceptible/exposed/recovered individuals
        else:
            if(self.rng.random() <= specificity):
                self.results = False
                pass
            else:
                self.results = True
                
        self.processing_results = True
        self.delay = geometric_by_mean(self.rng, test_results_delay)

    def get_test_results(self, time_to_recovery):
        '''After the delay in receiving test results, sets the
        `processing_results` boolean to `False`. Puts the node
        into quarantine if the test comes back positive.
        '''
        self.processing_results = False

        if(self.results):
            self.node.quarantine(time_to_recovery)
            
class Node:
    def __init__(self, rng, i):
        self.rng = rng

        self.index = i
        self.index_case = False

        self.nodes_infected = 0
        self.quarantine_time = 0
        self.symptoms = False

        self.state = 'susceptible'
        self.state_time = 0

        self.test = Test(rng, self)

    def __str__(self):
        return(self.state)

    def get_exposed(self):
        self.state = 'exposed'

        # Pull from geometric distribution with mean = `time_to_infection`
        self.state_time = geometric_by_mean(self.rng, time_to_infection)

    def get_infected(self, time_to_recovery):
        self.state = 'infected'

        # Pull from geometric distribution with mean = `time_to_recovery`
        self.state_time = geometric_by_mean(self.rng, time_to_recovery)

    def update(self, rng, global_time, spread_settings, test_settings, state_settings):
        '''Runs once per cycle per node, updating a node based on it's state.
        1. Susceptible: do nothing
        2. Exposed: change to infected state after mean incubation period (3 days)
        3. Infected:
        4. Recovered: do nothing
        '''
        # Update the amount of time we have left to spend in the current state
        self.state_time -= 1

        # Grab state settings
        time_to_infection       = state_settings['time_to_infection'] # A.K.A. incubation time
        time_to_recovery        = state_settings['time_to_recovery']
        symptoms_probability    = state_settings['symptoms_probability']
        #time_to_symptoms        = state_settings['time_to_symptoms']

        # Update test properties
        self.test.update(self, global_time, test_settings, time_to_recovery)

        # susceptible
        if(self.state == 'susceptible'):
            pass

        # exposed
        elif(self.state == 'exposed'):
            # Progress from exposed to infected state after mean incubation period (3 days)
            if(self.state_time == 0):
                self.get_infected(time_to_recovery)

        # infected
        if(self.state == 'infected'):
            # Progress from infected to recovered state after mean recovery time (14 days)
            if(self.state_time == 0):
                self.state = 'recovered'

            # If we are still infected...
            else:
                # Gain symptoms with some probability (0.30)
                if( not self.symptoms
                and rng.random() <= symptoms_probability):
                        self.symptoms = True

                # Spread if not quarantined
                if(self.quarantine_time == 0):
                    self.spread(spread_settings)

                # TODO(jordan): If symptomatic, die with some probability (0.0005)

        # recovered
        elif(self.state == 'recovered'):
            pass

    def spread(self, spread_settings):
        '''Spreads an infection with some probability `transmission_rate`
        to its neighboring nodes.
        '''
        neighbors = spread_settings['neighbors']
        nodes = spread_settings['nodes']
        transmission_rate = spread_settings['transmission_rate']
        
        # Iterate through the node's neighbors
        for neighbor_index in neighbors:
            # Select a specific neighboring node
            neighbor_node = nodes[neighbor_index]

            # Spread to this specific neighbor...
            if( neighbor_node.state == 'infected'           #       if the neighbor is susceptible
            and neighbor_node.quarantine_time == 0          # and   if the neighbor is not quarantined
            and self.rng.random() <= transmission_rate):    # and   if the random chance succeeds
                neighbor_node.get_exposed()

                # Count R0 cases (cases caused by index cases)
                if(self.index_case == True):
                    self.nodes_infected += 1

    def quarantine(self, time_to_recovery):
        '''If a node receives a positive test result, they will quarantine
        for a mean time of `14` (geometric distribution).
        '''
        # Pull from geometric distribution, mean recovery time = 14
        self.quarantine_time = geometric_by_mean(self.rng, time_to_recovery)

def add_exogenous_cases(nodes, amount, rng):
    '''Sets a number of cases specified by `amount` to exposed.
    This represents cases coming onto campus from outside sources,
    e.g. an individual getting infected while visiting home.
    '''
    # Susceptible nodes
    susceptible_nodes = [node.index for node in nodes if node.state == 'susceptible']
    
    # If there aren't enough susceptible nodes remaining to infected,
    # just expose the rest.
    if(len(susceptible_nodes) <= amount):
        for i in susceptible_nodes:
            nodes[i].getExposed()
        return

    # Randomly choose an `amount` of susceptible nodes to expose.
    # The `replace` parameter ensures we don't choose duplicates.
    chosen_indices = rng.choice(susceptible_nodes, amount, replace = False)
    for i in chosen_indices:
        nodes[i].get_exposed()

def run_simulation(graph, time_span, initial_infected_count, data, transmission_rate, exogenous_rate, test_rate):
    nodes = []
    for node_index in graph.nodes():
        nodes.append(Node(node_index))

    # Initialize numpy random number generator
    rng = np.random.default_rng()

    # Randomly infect `initial_infected_count` nodes
    initial_infected_nodes = rng.choice(len(nodes), initial_infected_count, replace = False)
    for chosen_node in initial_infected_count:
        node = nodes[chosen_node]
        node.change_state('infected')
        node.index_case = True

    for ti in range(time_span):
        # Add exogenous infections weekly, after the first week
        if(ti % 7 == 0 and ti > 0):
            add_exogenous_cases(nodes, exogenous_rate)
    
        # Daily counts
        infected, recovered, susceptible = 0, 0, 0
        for node in nodes:
            if(node.state == 0):
                susceptible += 1
            elif(node.state == 4):
                recovered += 1
            else:
                infected += 1

            node.update(rng, g.neighbors(node.index), nodes, transmission_rate, ti, test_rate)

        # Save data (["infected", "recovered", "susceptible"])
        for state in data:
            data[state] = data[state].append({'day': ti, 'cases': eval(state)}, ignore_index = True)

    totalRecovered = 0
    totalSpreadTo = 0
    totalTests = 0

    # rt calculating
    for node in nodes:
        totalTests += node.testsTaken
        if(node.indexCase):
            totalRecovered += 1
            totalSpreadTo += node.rt

    # return (rt, cost of tests)
    return((totalSpreadTo / totalRecovered), totalTests)

def simulationContainer(ax, testRate, rt, X, sampleSize):
    data = {
        "infected": pd.DataFrame(),
        "recovered": pd.DataFrame(),
        "susceptible": pd.DataFrame()
    }
    for i in range(TIME_HORIZON):
        for state in data:
            data[state].append([])
    
    transmissionRate = BASE_INFECTION_RATE[rt]
    expRt, testCost = 0, 0
    for i in range(sampleSize):
        result = runSimulation(TIME_HORIZON, X, data, transmissionRate, X, testRate)
        expRt += result[0]
        testCost += result[1]
    expRt /= sampleSize
    testCost = testCost * TEST_COST / sampleSize

    print("Test rate: %s, beta: %.2f%%, X: %d | Rt %d trials: %.2f" % (str(testRate), 100 * transmissionRate, X, sampleSize, expRt))

    for state in data:
        sns.lineplot(data = data[state], x = 'day', y = 'cases', ax = ax)

    # Calculate total (mean + std) infected + recovered
    dfInfected, dfRecovered = data["infected"], data["recovered"]
    dfTotalCases = dfInfected.loc[dfInfected['day'] == TIME_HORIZON - 1]['cases'] + dfRecovered.loc[dfRecovered['day'] == TIME_HORIZON - 1]['cases']
    meanTotalCases, stdTotalCases = dfTotalCases.mean(), dfTotalCases.std()

    ax.set_title(r"$R_t$: %.2f, C: %.2f, $\bar{x}$: %.1f, $\sigma_x$: %.1f" % (expRt, testCost, meanTotalCases, stdTotalCases))
