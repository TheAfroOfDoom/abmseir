###
# File: simulation.py
# Created: 01/25/2021
# Author: Jordan Williams (jwilliams13@umassd.edu)
# -----
# Last Modified: 02/16/2021
# Modified By: Jordan Williams
###

"""
Simulates the infectious spread across a community (graph) based on parameters defined in config.json.
"""

# Modules
from datetime import time
import config
from log_handler import logging as log

# Packages
import numpy as np
import pandas as pd

class Simulation:
    def __init__(self, g):
        self.rng = np.random.default_rng() # TODO(jordan): Log this seed
        self.graph = g
        self.nodes = self.generate_nodes()
        self.time_horizon = 100
        self.time = 0
        self.test_cost = 25
        self.exogenous_rate = 0
        self.initial_infected_count = 20

        beta = 1.5 * (1/14 + 3/98)
        self.transmission_rate = beta / 42#4999

        self.time_to_recovery = {'mean': 14, 'min': 10}

        self.all_states = [
            'susceptible',
            'exposed',
            'infected asymptomatic',
            'infected symptomatic',
            'recovered',
            'dead'
            ]
            
        self.data = self.generate_data_container()

        self.pre_step()
    
    def generate_nodes(self):
        nodes = []
        for node_index in self.graph.nodes():
            nodes.append(Node(self.rng, node_index))

        # TODO(aidan) May result in added time complexity, could be optimized
        for node in nodes:
            node.set_neighbors(self.graph.neighbors(node.index), nodes)

        return nodes

    def generate_data_container(self):
        data = pd.DataFrame(dtype = int, columns = self.all_states)
        return data

    def pre_step(self):
        # Randomly infect `initial_infected_count` nodes
        initial_infected_nodes = self.rng.choice(len(self.nodes), self.initial_infected_count, replace = False)
        for chosen_node_index in initial_infected_nodes:
            chosen_node = self.nodes[chosen_node_index]
            chosen_node.get_infected(self.time_to_recovery)
            chosen_node.index_case = True
        log.debug(initial_infected_nodes)

    def run_step(self):
        # Add exogenous infections weekly, after the first week
        if(self.time % 7 == 0 and self.time > 0):
            self.add_exogenous_cases(self.exogenous_rate)
    
        # Daily counts
        data_per_state = {}
        for state in self.all_states:
            data_per_state[state] = 0

        for node in self.nodes:
            data_per_state[node.state] += 1

            node.update(self.rng, self.time, self.transmission_rate)

        # Save data
        self.data = self.data.append(data_per_state, ignore_index = True)

        # Increment global time
        self.time += 1

    def calculate_r_0(self):            
        total_recovered, total_spread_to = 0, 0
        # R_0 calculating
        for node in self.nodes:
            if(node.index_case):
                total_recovered += 1
                total_spread_to += node.nodes_infected

        # Return R_0
        return(total_spread_to / total_recovered)

    def add_exogenous_cases(self, amount):
        '''Sets a number of cases specified by `amount` to exposed.
        This represents cases coming onto campus from outside sources,
        e.g. an individual getting infected while visiting home.
        '''
        # Susceptible nodes
        susceptible_nodes = [node.index for node in self.nodes if node.state == 'susceptible']
        
        # If there aren't enough susceptible nodes remaining to infected,
        # just expose the rest.
        if(len(susceptible_nodes) <= amount):
            for i in susceptible_nodes:
                self.nodes[i].get_exposed()
            return

        # Randomly choose an `amount` of susceptible nodes to expose.
        # The `replace` parameter ensures we don't choose duplicates.
        chosen_indices = self.rng.choice(susceptible_nodes, amount, replace = False)
        for i in chosen_indices:
            self.nodes[i].get_exposed()

    def calculate_infection_rate(self, node_degree, desired_rt, error):
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
            infection_rate = self.bisect(lower_bound, upper_bound)

            # Run simulation TODO(jordan): <until all Gen.1 infections recover and save measured Rt>
            # TODO(jordan): Get the average `measured_rt` of multiple simulations.
            measured_rt = self.run_simulation()

            # Update bounds
            if(measured_rt > desired_rt + error):
                upper_bound = infection_rate
            elif(measured_rt < desired_rt - error):
                lower_bound = infection_rate
            # Break when we measure an rt within the error of our desired_rt
            else:
                break

        return(infection_rate)

class Node:
    def __init__(self, rng, i):
        # Node parameters
        self.rng = rng
        self.time_to_infection       = 3 # -change-
        self.time_to_recovery        = {'mean': 14, 'min': 10} # -change-
        symptoms_probability = 0.3
        self.symptoms_rate    = (symptoms_probability / (1 - symptoms_probability)) / self.time_to_recovery['mean'] # -change-
        death_probability = 0.0005
        self.death_rate    = (death_probability / (1 - death_probability)) / self.time_to_recovery['mean'] # -change-

        # Run-time initialized
        self.index = i
        self.index_case = False
        self.neighbors = []
        self.test = Test(rng, self)

        # Node variables
        self.nodes_infected = 0
        self.quarantine_time = 0
        self.state = 'susceptible'
        self.state_time = 0

    def __str__(self):
        return(self.state)

    def set_neighbors(self, neighbor_indices, nodes):
        for i in neighbor_indices:
            self.neighbors.append(nodes[i])

    def get_exposed(self):
        self.state = 'exposed'

        # Pull from geometric distribution with mean = `time_to_infection`
        self.state_time = geometric_by_mean(self.rng, 3) # -change-

    def get_infected(self, time_to_recovery):
        self.state = 'infected asymptomatic'

        # Pull from geometric distribution with mean = `time_to_recovery`
        self.state_time = geometric_by_mean(self.rng, time_to_recovery['mean'], time_to_recovery['min'])
        #log.info("Node %d TTR: %d" % (self.index, self.state_time))

    def update(self, rng, global_time, transmission_rate):
        '''Runs once per cycle per node, updating a node based on it's state.
        1. Susceptible: do nothing
        2. Exposed: change to infected state after mean incubation period (3 days)
        3. Infected:
        4. Recovered: do nothing
        '''
        # Update the amount of time we have left to spend in the current state
        if(self.state_time > 0):
            self.state_time -= 1

        # Update test properties
        self.test.update(global_time, self.time_to_recovery)

        # susceptible
        if(self.state == 'susceptible'):
            pass

        # exposed
        elif(self.state == 'exposed'):
            # Progress from exposed to infected state after mean incubation period (3 days)
            if(self.state_time == 0):
                self.get_infected(self.time_to_recovery)

        # infected asymptomatic
        if(self.state == 'infected asymptomatic'):
            # Progress from infected to recovered state after mean recovery time (14 days)
            if(self.state_time == 0):
                self.state = 'recovered'

            # If we are still infected...
            else:
                # Gain symptoms with some probability (0.30)
                if(rng.random() <= self.symptoms_rate):
                    self.state = 'infected symptomatic'

                # Spread if not quarantined
                elif(self.quarantine_time == 0):
                    self.spread(transmission_rate)

        # infected symptomatic
        if(self.state == 'infected symptomatic'):
            # Progress from infected to recovered state after mean recovery time (14 days)
            if(self.state_time == 0):
                self.state = 'recovered'

            # If we are still infected...
            elif(rng.random() <= self.death_rate):
                self.state = 'dead'

        # recovered
        elif(self.state == 'recovered'):
            pass

    def spread(self, transmission_rate):
        '''Spreads an infection with some probability `transmission_rate`
        to its neighboring nodes.
        '''
        
        # Iterate through the node's neighbors
        for neighbor in self.neighbors:

            # Spread to this specific neighbor...
            if( neighbor.state == 'susceptible'           #       if the neighbor is susceptible
            and neighbor.quarantine_time == 0          # and   if the neighbor is not quarantined
            and self.rng.random() <= transmission_rate):    # and   if the random chance succeeds
                neighbor.get_exposed()

                # Count R_0 cases (cases caused by index cases)
                if(self.index_case == True):
                    self.nodes_infected += 1

    def quarantine(self, time_to_recovery):
        '''If a node receives a positive test result, they will quarantine
        for a mean time of `14` (geometric distribution).
        '''
        # Pull from geometric distribution, mean recovery time = 14
        self.quarantine_time = time_to_recovery['mean'] #geometric_by_mean(self.rng, time_to_recovery)

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

        # Test settings
        self.sensitivity = 0.7
        self.specificity = 0.98
        self.results_delay = 1
        self.rate = 0

    def update(self, global_time, time_to_recovery):
        '''Runs once per cycle per node, updating its test information as follows:
        1. Waits for the test result's delay
            - Updates its node based on the results
        2. 
        '''

        # If we are waiting on the latest test results, decrement the delay we are waiting
        if(self.processing_results):
            self.delay -= 1

        # Determine if we should get tested                             # Only test if:
        bool_should_get_tested  =   (self.rate != 0                     #       `self.rate` is not 0
                                and global_time % self.rate == 0)       # and   if the current `global_time` is
                                                                        #       divisible by our `self.rate`
        bool_should_get_tested &=   global_time > 0                     # and   if this isn't the first day of the simulation
        bool_should_get_tested &=   self.node.quarantine_time == 0      # and   if we aren't already in quarantine

        # Get tested if the above conditions pass
        if(bool_should_get_tested):
            self.take()

        # Receive test results Y days after being tested (if not quarantined)
        if(self.processing_results
        and self.delay == 0):
            self.get_test_results(time_to_recovery)

    def take(self):
        '''Simulates a node taking a COVID test.
        Returns a boolean based on sensitivity/specificity parameters
        and whether or not the node is actually infected or not.
        '''

        # Increment the amount of tests this node has taken
        self.count += 1

        # Use positive rates for infected individuals
        if(self.node.state == 'infected asymptomatic'):
            if(self.rng.random() <= self.sensitivity):
                self.results = True
            else:
                self.results = False
                pass

        # Use negative rates for susceptible individuals
        elif(self.node.state in [
            # TODO(jordan): Paltiel only tests S/Ia nodes. Should our UMassD model test more types of nodes?
            'susceptible'
            #'susceptible', 'exposed', 'recovered'
        ]):
            if(self.rng.random() <= self.specificity):
                self.results = False
                pass
            else:
                self.results = True
                
        self.processing_results = True
        self.delay = geometric_by_mean(self.rng, self.results_delay)

    def get_test_results(self, time_to_recovery):
        '''After the delay in receiving test results, sets the
        `processing_results` boolean to `False`. Puts the node
        into quarantine if the test comes back positive.
        '''
        self.processing_results = False

        if(self.results):
            self.node.quarantine(time_to_recovery)

def geometric_by_mean(rng, mean, min = 0):
    # https://en.wikipedia.org/wiki/Geometric_distribution (mean = 1 / p)
    p = 1 / (mean - min)

    return(rng.geometric(p) + min)

def bisect(lo, hi):
    '''Returns the average of two numeric parameters.
    '''
    return (lo + hi) / 2