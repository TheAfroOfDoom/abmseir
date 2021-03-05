###
# File: simulation.py
# Created: 01/25/2021
# Author: Jordan Williams (jwilliams13@umassd.edu)
# -----
# Last Modified: 03/04/2021
# Modified By: Jordan Williams
###

"""
Simulates the infectious spread across a community (graph) based on parameters defined in config.json.
"""

# Modules
from log_handler import logging as log

# Packages
import numpy as np
import pandas as pd

class Simulation: 
    def __init__(self, g):
        self.all_states = [
            'susceptible',
            'exposed',
            'infected asymptomatic',
            'infected symptomatic',
            'recovered',
            'dead'
            ]
        
        # Simulation constants
        self.rng = np.random.default_rng() # TODO(jordan): Log this seed
        self.graph = g
        self.nodes = self.generate_nodes()

        # Simulation parameters
        self.set_parameters()

        # Simulation data
        self.data = self.generate_data_container()
        self.time = 0
    
    def get_mean_node_degree(self):
        # TODO(jordan): This seems really janky...
        # https://networkx.org/documentation/stable/reference/classes/generated/networkx.Graph.degree.html
        mean_degree = np.mean([degree[1] for degree in self.graph.degree])
        return(mean_degree)

    def set_parameters(self, args = None):
        '''Update parameters via a dict argument `args`.
        Forces re-calculation of dependent parameters.
        '''
        # Hard-coded COVID-19 values
        if(args is None):
            log.debug("Default args passed.")
            # Population
            self.population_size = len(self.graph)
            #self.population_size = 1000 # TODO(jordan): Verify that this is equal to graph size
            self.initial_infected_count = 10

            self.cycles_per_day = 3
            self.time_horizon = 80 * self.cycles_per_day

            self.exogenous_amount = 5
            self.exogenous_frequency = 7 * self.cycles_per_day

            # Disease
            self.r0 = 1.5

        else:
            log.debug("Non-default args passed.")
            # Update attribute if it already exists in Simulation class
            for k, v, in args.items():
                if hasattr(self, k):
                    self.__dict__.update({k: v})
            
            # Recalculate dependents
            keys = args.keys()

            # time horizon
            if(any(key in keys for key in ['cycles_per_day', 'time_horizon'])):
                self.time_horizon = args['time_horizon'] * self.cycles_per_day

            # exogenous frequency
            if(any(key in keys for key in ['cycles_per_day', 'exogenous_frequency'])):
                self.exogenous_frequency = args['exogenous_frequency'] * self.cycles_per_day

        # Calculate mean_node_degree once ahead of time so each node doesn't have to do it
        mean_node_degree = self.get_mean_node_degree()

        # Pass params to nodes
        for node in self.nodes:
            node.set_parameters(args, self.cycles_per_day, self.r0, mean_node_degree)
    
    def get_parameters(self, all = False):
        params = {
            'population_size': self.population_size,
            'initial_infected_count': self.initial_infected_count,

            'cycles_per_day': self.cycles_per_day,
            'time_horizon': self.time_horizon,

            'exogenous_amount': self.exogenous_amount,
            'exogenous_frequency': self.exogenous_frequency,

            'r0': self.r0
        }
        if(all):
            # Put params into one dict
            params.update(self.nodes[0].get_parameters(all = True))
            
        return(params)

    def generate_nodes(self):
        nodes = []
        for node_index in self.graph.nodes():
            nodes.append(Node(self.rng, node_index))

        # TODO(aidan) May result in added time complexity, could be optimized
        for node in nodes:
            node.set_neighbors(self.graph.neighbors(node.index), nodes)

        return nodes

    def generate_data_container(self):
        cols = ['day']
        cols.extend(self.all_states)
        data = pd.DataFrame(dtype = int, columns = cols)
        return data

    def pre_step(self):
        # Randomly infect `initial_infected_count` nodes
        initial_infected_nodes = self.rng.choice(len(self.nodes), self.initial_infected_count, replace = False)
        for chosen_node_index in initial_infected_nodes:
            chosen_node = self.nodes[chosen_node_index]
            chosen_node.get_infected()
            chosen_node.index_case = True

        log.debug(initial_infected_nodes)

    def run_step(self):
        # Add exogenous infections weekly, after the first week
        if(self.time % self.exogenous_frequency == 0 and self.time != 0):
            self.add_exogenous_cases(self.exogenous_amount)

        # Update each node
        for node in self.nodes:
            node.update(self.rng, self.time)
    
        # Count each state and add to daily data
        self.count_states(self.time)

        # Increment global time
        self.time += 1
    
    def run(self):
        self.pre_step()
        for _ in range(self.time_horizon):
            self.run_step()

    def count_states(self, t):
        # Daily counts
        data_per_state = {}
        for state in self.all_states:
            data_per_state[state] = 0
        data_per_state['day'] = int(t)

        for node in self.nodes:
            data_per_state[node.state] += 1

        # Save data
        self.data = self.data.append(data_per_state, ignore_index = True)

    def calculate_r0(self):            
            total_recovered, total_spread_to = 0, 0
            # R0 calculating
            for node in self.nodes:
                if(node.index_case):
                    total_recovered += 1
                    total_spread_to += node.nodes_infected

            # Return R0
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

    def export_data(self):
        return(self.data.to_csv(line_terminator = '\n'))

class Node:
    def __init__(self, rng, i):
        # Node parameters
        self.rng = rng

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

    def set_parameters(self, args = None, cycles_per_day = 1, r0 = None, mean_node_degree = None):
        '''Update parameters via a dict argument `args`.
        '''
        # Hard-coded COVID-19 values
        if(args is None):
            self.time_to_infection = {  # i.e. incubation time
                'mean': 3 * cycles_per_day,
                'min': 0 * cycles_per_day
                }
            self.time_to_recovery = {
                'mean': 14 * cycles_per_day,
                'min': 0 * cycles_per_day
                }

            self.probability_of_symptoms = 0.30
            self.symptoms_rate = (self.probability_of_symptoms / (1 - self.probability_of_symptoms)) / self.time_to_recovery['mean']

            self.probability_of_death_given_symptoms = 0.0005
            self.death_rate = (self.probability_of_death_given_symptoms / (1 - self.probability_of_death_given_symptoms)) / self.time_to_recovery['mean']
            #self.probability_of_death_given_symptoms * self.symptoms_rate * (self.symptoms_rate + self.time_to_recovery['mean']) / (((1 - self.probability_of_death_given_symptoms) * self.symptoms_rate) - (self.probability_of_death_given_symptoms * self.time_to_recovery['mean']))
                              
            self.beta = r0 * ((1 / self.time_to_recovery['mean']) + self.symptoms_rate)
            self.transmission_rate = self.beta / mean_node_degree

        else:
            # Update attribute if it already exists in Simulation class
            for k, v, in args.items():
                if hasattr(self, k):
                    self.__dict__.update((k, v))
            
            # Recalculate dependents
            keys = args.keys()

            # incubation rate
            if(any(key in keys for key in ['cycles_per_day', 'time_to_infection'])):
                self.time_to_infection = {
                    'mean': self.time_to_infection['mean'] * cycles_per_day,
                    'min': self.time_to_infection['min'] * cycles_per_day
                }

            # recovery rate
            if(any(key in keys for key in ['cycles_per_day', 'time_to_recovery'])):
                self.time_to_recovery = {
                    'mean': self.time_to_recovery['mean'] * cycles_per_day,
                    'min': self.time_to_recovery['min'] * cycles_per_day
                }

            # symptoms rate
            if(any(key in keys for key in ['cycles_per_day', 'time_to_recovery', 'probability_of_symptoms'])):
                self.symptoms_rate = (self.probability_of_symptoms / (1 - self.probability_of_symptoms)) / self.time_to_recovery['mean']

            # death rate
            if(any(key in keys for key in ['cycles_per_day', 'time_to_recovery', 'probability_of_death_given_symptoms'])):
                self.death_rate = (self.probability_of_death_given_symptoms / (1 - self.probability_of_death_given_symptoms)) / self.time_to_recovery['mean']

            # transmission rate
            if(any(key in keys for key in ['cycles_per_day', 'time_to_recovery', 'probability_of_symptoms', 'r0'])):
                self.beta = r0 * ((1 / self.time_to_recovery['mean']) + self.symptoms_rate)
                self.transmission_rate = self.beta / mean_node_degree

        # Pass params to corresponding Test object
        self.test.set_parameters(args, cycles_per_day)

    def get_parameters(self, all = False):
        params = {
            'time_to_infection': self.time_to_infection,
            'time_to_recovery': self.time_to_recovery,

            'probability_of_symptoms': self.probability_of_symptoms,
            'symptoms_rate': self.symptoms_rate,

            'probability_of_death_given_symptoms': self.probability_of_death_given_symptoms,
            'death_rate': self.death_rate,

            'beta': self.beta,
            'transmission_rate': self.transmission_rate
        }
        if(all):
            # Put params into one dict
            params.update(self.test.get_parameters())
        
        return(params)

    def set_neighbors(self, neighbor_indices, nodes):
        for i in neighbor_indices:
            self.neighbors.append(nodes[i])

    def get_exposed(self):
        self.state = 'exposed'

        # Pull from geometric distribution with mean = `time_to_infection`
        self.state_time = geometric_by_mean(self.rng, self.time_to_infection['mean'], self.time_to_infection['min'])

    def get_infected(self):
        self.state = 'infected asymptomatic'

        # Pull from geometric distribution with mean = `time_to_recovery`
        self.state_time = geometric_by_mean(self.rng, self.time_to_recovery['mean'], self.time_to_recovery['min'])

    def update(self, rng, global_time):
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

        # States that don't do anything (this will probably save on runtime)
        # susceptible/recovered/dead
        if(self.state == 'susceptible'
        or  self.state == 'recovered'
        or  self.state == 'dead'):
            pass

        else:
            # exposed
            if(self.state == 'exposed'):
                # Progress from exposed to infected state after mean incubation period (3 days)
                if(self.state_time == 0):
                    self.get_infected()

            # infected asymptomatic
            if(self.state == 'infected asymptomatic'):
                # Spread if not quarantined
                if(self.quarantine_time == 0):
                    self.spread()

                # Gain symptoms with some probability (0.30) at a calculated rate
                if(rng.random() < self.symptoms_rate):
                    self.state = 'infected symptomatic'
                    
                # Progress from infected to recovered state after mean recovery time (14 days)
                if(self.state_time == 0):
                    self.state = 'recovered'

            # infected symptomatic
            if(self.state == 'infected symptomatic'):
                # Die with some probability (0.0005) at a calculated rate
                if(rng.random() < self.death_rate):
                    self.state = 'dead'

                # Progress from infected to recovered state after mean recovery time (14 days)
                elif(self.state_time == 0):
                    self.state = 'recovered'

    def spread(self):
        '''Spreads an infection with some probability `transmission_rate`
        to its neighboring nodes.
        '''
        # Iterate through the node's neighbors
        for neighbor in self.neighbors:
    
            # Spread to this specific neighbor...
            if( neighbor.state == 'susceptible'                 #       if the neighbor is susceptible
            and neighbor.quarantine_time == 0                   # and   if the neighbor is not quarantined
            and self.rng.random() < self.transmission_rate):   # and   if the random chance succeeds
                neighbor.get_exposed()

                # Count R0 cases (cases caused by index cases)
                if(self.index_case == True):
                    self.nodes_infected += 1

    def quarantine(self, time_to_recovery):
        '''If a node receives a positive test result, they will quarantine
        for a mean time of `14` (geometric distribution).
        '''
        # Pull from geometric distribution, mean recovery time = 14
        self.quarantine_time = time_to_recovery['mean'] #geometric_by_mean(self.rng, time_to_recovery)
        # TODO(jordan): Ask Dr. Fine how long people are put in quarantine for
        # * min. 14 days no matter what? (implemented)
        # * until symptoms subside?

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

    def set_parameters(self, args = None, cycles_per_day = 1):
        '''Update parameters via a dict argument `args`.
        '''
        # Hard-coded COVID-19 values
        if(args is None):
            self.specificity = 0.98
            self.sensitivity = 0.9
            self.cost = 25
            self.results_delay = 1 * cycles_per_day
            self.rate = 0 * cycles_per_day

        else:
            for k, v, in args.items():
                if hasattr(self, k):
                    # Update attribute if it already exists in Simulation class
                    self.__dict__.update((k, v))
            
            # Recalculate dependents
            keys = args.keys()

            # results delay
            if(any(key in keys for key in ['cycles_per_day', 'results_delay'])):
                self.results_delay = self.results_delay * cycles_per_day

            # rate
            if(any(key in keys for key in ['cycles_per_day', 'rate'])):
                self.rate = self.rate * cycles_per_day

    def get_parameters(self):
        return({
            'specificity': self.specificity,
            'sensitivity': self.sensitivity,
            'cost': self.cost,
            'results_delay': self.results_delay,
            'rate': self.rate
        })

    def update(self, global_time, time_to_recovery):
        '''Runs once per cycle per node, updating its test information as follows:
        1. Waits for the test result's delay
            - Updates its node based on the results
        2. 
        '''

        # Don't get tested if dead/recovered

        # If we are waiting on the latest test results, decrement the delay we are waiting
        if(self.processing_results):
            self.delay -= 1

        # Determine if we should get tested
                                                                        # Only test if:
        bool_should_get_tested  =   (self.rate != 0                     #       `self.rate` is not 0
                                and global_time % self.rate == 0)       # and   if the current `global_time` is
                                                                        #       divisible by our `self.rate`
        bool_should_get_tested &=   global_time > 0                     # and   if this isn't the first day of the simulation
        bool_should_get_tested &=   self.node.quarantine_time == 0      # and   if we aren't already in quarantine
        bool_should_get_tested &=   (self.node.state != 'recovered'     # and   if node is not recovered/dead (those who already had infection will always test positive [FP])
                                    and self.node.state != 'dead')

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
        if(self.node.state == 'infected asymptomatic'
        #or self.node.state == 'infected'
        ):
            if(self.rng.random() < self.sensitivity):
                self.results = True
            else:
                self.results = False
                pass

        # Use negative rates for susceptible/exposed/recovered individuals
        else:
            if(self.rng.random() < self.specificity):
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
