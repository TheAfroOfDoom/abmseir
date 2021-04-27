###
# File: simulation.py
# Created: 01/25/2021
# Author: Jordan Williams (jwilliams13@umassd.edu)
# -----
# Last Modified: 04/26/2021
# Modified By: Jordan Williams
###

"""
Simulates the infectious spread across a community (graph) based on parameters defined in config.json.
"""

# Modules
from log_handler import logging as log

# Packages
import datetime
import numpy as np
import pandas as pd
from typing import List, Set

class Simulation:
    def __init__(self, g):
        self.all_states = [
            'susceptible',
            'exposed',
            'infected asymptomatic',
            'infected symptomatic',
            'recovered',
            'deceased'
            ]
        
        # Simulation constants
        self.rng = np.random.default_rng() # type: ignore # TODO(jordan): Log this seed
        self.graph = g
        self.old_index, self.new_index = 0, 1
        self.nodes = [[], []]   # type: List[List[Node]]
        self.nodes[self.old_index] = self.generate_nodes()
        self.nodes[self.new_index] = self.generate_nodes()
        self.previous_infected_nodes = self.current_infected_nodes = set() # type: Set[int]

        # Simulation parameters
        self.set_parameters()

        # Simulation data
        self.data = self.generate_data_container()
        self.time_index = 0

    def add_exogenous_cases(self, amount, time):
        '''Sets a number of cases specified by `amount` to exposed.
        This represents cases coming onto campus from outside sources,
        e.g. an individual getting infected while visiting home.
        '''
        nodes = self.nodes[self.new_index]
        # Susceptible nodes
        susceptible_nodes = [node.index for node in nodes if node.state == 'susceptible']
        
        # If there aren't enough susceptible nodes remaining to infected,
        # just expose the rest.
        if(len(susceptible_nodes) <= amount):
            for i in susceptible_nodes:
                nodes[i].exogenous = time
            return

        # Randomly choose an `amount` of susceptible nodes to expose.
        # The `replace` parameter ensures we don't choose duplicates.
        chosen_indices = self.rng.choice(susceptible_nodes, amount, replace = False)
        for i in chosen_indices:
            nodes[i].exogenous = time

    def calculate_r0(self):
        total_gens = {}
        nodes = self.nodes[self.old_index]
        # R0 calculating
        for node in nodes:
            gen = str(node.generation)
            if(gen not in total_gens.keys()):
                total_gens[gen] = 0
            total_gens[gen] += 1

        # Return R0
        return(total_gens)
        
    def count_states(self, t):
        nodes = self.nodes[self.new_index]
        # Count data structure
        data_per_state = {}
        for state in self.all_states:
            data_per_state[state] = 0
        data_per_state['day'] = int(t)

        # Daily counts
        for node in nodes:
            data_per_state[node.state] += 1

        # Save data
        self.data = self.data.append(data_per_state, ignore_index = True)
    
    def export_columns(self):
        return(['day'].extend(self.all_states))

    def export_data(self):
        return(self.data.to_csv(line_terminator = '\n'))

    def generate_data_container(self):
        data = pd.DataFrame(dtype = int, columns = self.export_columns())
        return(data)

    def generate_nodes(self):
        nodes = []    # type: List[Node]
        for node_index in self.graph.nodes():
            nodes.append(Node(self.rng, node_index))

        # TODO(aidan) May result in added time complexity, could be optimized
        for node in nodes:
            node.set_neighbors({i for i in self.graph.neighbors(node.index)})

        return(nodes)

    def get_mean_node_degree(self):
        # TODO(jordan): This seems really janky...
        # https://networkx.org/documentation/stable/reference/classes/generated/networkx.Graph.degree.html
        mean_degree = np.mean([degree[1] for degree in self.graph.degree])
        return(mean_degree)
        
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
            params.update(self.nodes[self.old_index][0].get_parameters(all = True))
            
        return(params)

    def link_nodes(self, node_0, node_1):
        node_0.twin = node_1
        node_1.twin = node_0

        node_0.test.twin = node_1.test
        node_1.test.twin = node_0.test

    def pre_step(self):
        # Randomly infect `initial_infected_count` nodes
        old_nodes = self.nodes[self.old_index]
        initial_infected_nodes = self.rng.choice(len(old_nodes), self.initial_infected_count, replace = False)
        for chosen_node_index in initial_infected_nodes:
            chosen_node = old_nodes[chosen_node_index]
            chosen_node.get_infected(self.current_infected_nodes)
            chosen_node.generation = 1

        log.debug(initial_infected_nodes)

        # Generate new nodes
        new_nodes = self.nodes[self.new_index]
        for index in range(len(old_nodes)):
            # Copy old nodes base params to new nodes
            old_nodes[index].copy(new_nodes[index], init = True)
            
            # Link twin nodes across old/new boundary
            self.link_nodes(old_nodes[index], new_nodes[index])

    def run(self):
        t0 = datetime.datetime.now()    # start of sim
        self.pre_step()
        for _ in range(self.time_horizon):
            self.run_step()
        t1 = datetime.datetime.now()    # end of sim
        self.time = (t0, t1)            # (start, end)

    def run_step(self):
        # Add exogenous infections weekly, after the first day
        if(self.time_index % self.exogenous_frequency == 0 and self.time_index != 0):
            self.add_exogenous_cases(self.exogenous_amount, self.time_index)

        # Update list of infected nodes
        self.previous_infected_nodes = self.current_infected_nodes.copy()

        # Update each node
        old_nodes, new_nodes = self.nodes[self.old_index], self.nodes[self.new_index]
        for node in new_nodes:
            node.update(self.rng, self.time_index, old_nodes, [self.previous_infected_nodes, self.current_infected_nodes])
    
        # Count each state and add to daily data
        self.count_states(self.time_index)

        # Increment global time
        self.time_index += 1

        # Swap indices
        self.old_index, self.new_index = self.new_index, self.old_index
    
    def set_parameters(self, args = None, nodes = None):
        '''Update parameters via a dict argument `args`.
        Forces re-calculation of dependent parameters.
        '''
        # Hard-coded COVID-19 values
        if(args is None):
            log.debug("Default args passed.")
            # Population
            self.population_size        = len(self.graph)
            self.initial_infected_count = 10

            self.cycles_per_day = 3
            self.time_horizon   = 80 * self.cycles_per_day

            self.exogenous_amount       = 25
            self.exogenous_frequency    = 7 * self.cycles_per_day

            # Disease
            self.r0 = 3.5

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

        # Pass params to nodes.
        for node in (nodes or self.nodes[self.old_index] + self.nodes[self.new_index]):
            node.set_parameters(args, self.cycles_per_day, self.r0, mean_node_degree)

class Node:
    def __init__(self, rng, i):
        # Node parameters
        self.rng = rng

        # Run-time initialized
        self.index = i              # type: int
        self.generation = 0         # Uninfected
        self.neighbors = set()      # type: Set[int]
        self.test = Test(rng, self)

        # Node variables
        self.exogenous = -1 # -1: not an exogenous case
        self.quarantine_time = 0
        self.state = 'susceptible'
        self.state_time = 0

    def contract(self, nodes, previous_infected_nodes):
        '''Contracts infection with some probability `transmission_rate`
        from neighboring Nodes.
        '''
        twin = self.twin    # type: ignore

        # If we are quarantined, we can't contract the virus
        if(self.quarantine_time > 0):
            return

        # Iterate through the prev. time step's infected neighbors
        #for neighbor in [neighbor for neighbor in twin.neighbors if neighbor.state == 'infected asymptomatic']:
        #for infected_node in [nodes[index] for index in previous_infected_nodes]:
        for infected_neighbor in [nodes[infected_index] for infected_index in previous_infected_nodes.intersection(twin.neighbors)]:

            # Contract the virus from this node...
            if( infected_neighbor.quarantine_time == 0                       #       if the neighbor is not quarantined
            and self.rng.random() < infected_neighbor.transmission_rate):    # and   if the random chance succeeds
                # Get exposed
                self.get_exposed()

                # Track which generation this is
                self.generation = infected_neighbor.generation + 1

                return

    def copy(self, dest, init = False):
        '''Copies specific parameters from this `Node` onto a destination `Node`.
        '''
        # base params are only copied once at the start during `pre_step()`
        if(init):
            dest.generation = self.generation

            # Also copy Test base params
            self.test.copy(dest.test, init = True)

        else:
            dest.generation         = self.generation
            dest.quarantine_time    = self.quarantine_time
            dest.state              = self.state
            dest.state_time         = self.state_time

            # Also copy Test params
            self.test.copy(dest.test)

    def get_exposed(self):
        # Get exposed
        self.state = 'exposed'
        self.state_time = geometric_by_mean(self.rng, self.time_to_infection_mean, self.time_to_infection_min)

    def get_infected(self, current_infected_nodes):
        self.state = 'infected asymptomatic'

        # Pull from geometric distribution with mean = `time_to_recovery`
        self.state_time = geometric_by_mean(self.rng, self.time_to_recovery_mean, self.time_to_recovery_min)

        # Add self to list of `current_infected_nodes`
        current_infected_nodes.add(self.index)

    def get_parameters(self, all = False):
        params = {
            'cycles_per_day': self.cycles_per_day,
            'r0': self.r0,

            'time_to_infection_mean': self.time_to_infection_mean,
            'time_to_infection_min': self.time_to_infection_min,

            'time_to_recovery_mean': self.time_to_recovery_mean,
            'time_to_recovery_min': self.time_to_recovery_min,

            'symptoms_probability': self.symptoms_probability,
            'symptoms_rate': self.symptoms_rate,

            'death_probability': self.death_probability,
            'death_rate': self.death_rate,

            'beta': self.beta,
            'transmission_rate': self.transmission_rate
        }
        if(all):
            # Put params into one dict
            params.update(self.test.get_parameters())
        
        return(params)

    def get_uninfected(self, current_infected_nodes):
        # Remove self from list of `current_infected_nodes`
        current_infected_nodes.remove(self.index)

    def quarantine(self, time_to_recovery_mean):
        '''If a node receives a positive test result, they will quarantine
        for a mean time of `14` (geometric distribution).
        '''
        # 14 days flat
        self.quarantine_time = time_to_recovery_mean

    def set_neighbors(self, neighbor_indices):
        #for i in neighbor_indices:
        #    self.neighbors.append(nodes[i])
        self.neighbors = neighbor_indices

    def set_parameters(self, args = None, cycles_per_day = 1, r0 = None, mean_node_degree = None):
        '''Update parameters via a dict argument `args`.
        '''
        # Hard-coded COVID-19 values
        if(args is None):
            self.cycles_per_day = cycles_per_day
            self.r0 = r0

            # i.e. incubation time
            self.time_to_infection_mean = 3 * cycles_per_day
            self.time_to_infection_min = 0 * cycles_per_day

            self.time_to_recovery_mean = 14 * cycles_per_day
            self.time_to_recovery_min = 0 * cycles_per_day

            self.symptoms_probability = 0.30
            self.symptoms_rate = (self.symptoms_probability / (1 - self.symptoms_probability)) / self.time_to_recovery_mean

            self.death_probability = 0.0005
            self.death_rate = (self.death_probability / (1 - self.death_probability)) / self.time_to_recovery_mean

            self.beta = r0 * ((1 / self.time_to_recovery_mean) + self.symptoms_rate)
            self.transmission_rate = self.beta / mean_node_degree

        else:
            # Update attribute if it already exists in Node class
            for k, v, in args.items():
                if hasattr(self, k):
                    setattr(self, k, v)
            
            # Recalculate dependents
            keys = args.keys()

            # incubation rate
            if(any(key in keys for key in ['cycles_per_day', 'time_to_infection_mean', 'time_to_infection_min'])):
                self.time_to_infection_mean = self.time_to_infection_mean * cycles_per_day
                self.time_to_infection_min = self.time_to_infection_min * cycles_per_day

            # recovery rate
            if(any(key in keys for key in ['cycles_per_day', 'time_to_recovery_mean', 'time_to_recovery_min'])):
                self.time_to_recovery_mean = self.time_to_recovery_mean * cycles_per_day
                self.time_to_recovery_min = self.time_to_recovery_min * cycles_per_day

            # symptoms rate
            if(any(key in keys for key in ['cycles_per_day', 'time_to_recovery_mean', 'time_to_recovery_min', 'symptoms_probability'])):
                self.symptoms_rate = (self.symptoms_probability / (1 - self.symptoms_probability)) / self.time_to_recovery_mean

            # death rate
            if(any(key in keys for key in ['cycles_per_day', 'time_to_recovery_mean', 'time_to_recovery_min', 'death_probability'])):
                self.death_rate = (self.death_probability / (1 - self.death_probability)) / self.time_to_recovery_mean

            # transmission rate
            if(any(key in keys for key in ['cycles_per_day', 'time_to_recovery_mean', 'time_to_recovery_min', 'symptoms_probability', 'r0'])):
                self.beta = r0 * ((1 / self.time_to_recovery_mean) + self.symptoms_rate)
                self.transmission_rate = self.beta / mean_node_degree

        # Pass params to corresponding Test object
        self.test.set_parameters(args, cycles_per_day)

    def update(self, rng, global_time, nodes, infected_nodes):
        '''Runs once per cycle per node, updating a node based on its twin (prev. time step) and neighbors.
        1. Susceptible: do nothing
        2. Exposed: change to infected state after mean incubation period (3 days)
        3. Infected: spread, gain symptoms, die, etc.
        4. Recovered/Deceased: do nothing
        '''
        # Copy params from previous time step
        twin = self.twin    # type: ignore
        twin.copy(self)

        previous_infected_nodes, current_infected_nodes = infected_nodes

        # Update the amount of time we have left to spend in the current state
        if(self.state_time > 0):
            self.state_time -= 1

        # Update test properties
        self.test.update(global_time, self.time_to_recovery_mean)

        # susceptible
        if(self.state == 'susceptible'):
            # If we have been marked as an exogenous case, gain infection
            if(self.exogenous >= 0):
                self.get_exposed()

            # Otherwise, contract infection with some probability from neighbors
            else:
                self.contract(nodes, previous_infected_nodes)

            return

        # exposed
        elif(self.state == 'exposed'):
            # Progress from exposed to infected state after mean incubation period (3 days)
            if(self.state_time == 0):
                self.get_infected(current_infected_nodes)
            return

        # infected asymptomatic
        elif(self.state == 'infected asymptomatic'):
            # Progress from infected to recovered state after mean recovery time (14 days)
            if(self.state_time == 0):
                self.state = 'recovered'
                self.get_uninfected(current_infected_nodes)

            # Gain symptoms with some probability (0.30) at some rate
            elif(rng.random() < self.symptoms_rate):
                self.state = 'infected symptomatic'
                self.get_uninfected(current_infected_nodes)
            return

        # infected symptomatic
        elif(self.state == 'infected symptomatic'):
            # Progress from infected to recovered state after mean recovery time (14 days)
            if(self.state_time == 0):
                self.state = 'recovered'

            # Die with some probability (0.0005) at some rate
            elif(rng.random() < self.death_rate):
                self.state = 'deceased'

            return

        # recovered/deceased
        else:
            #elif(self.state == 'recovered'
            #or  self.state == 'deceased'):
            return

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
        self.node = node    # type: Node

        # Number of tests this node has taken
        self.count = 0

        # True means the test indicated infection in the individual
        self.results = True

        # Time this node needs to wait until it gets its test results
        self.delay = 0
        self.processing_results = False

    def copy(self, dest, init = False):
        '''Copies specific parameters from this `Test` onto a destination `Test`.
        '''
        if(init):
            pass

        else:
            dest.count      = self.count
            dest.results    = self.results
            dest.delay      = self.delay
            dest.processing_results = self.processing_results

    def get_parameters(self):
        return({
            'cycles_per_day': self.cycles_per_day,
            'specificity': self.specificity,
            'sensitivity': self.sensitivity,
            'cost': self.cost,
            'results_delay': self.results_delay,
            'rate': self.rate
        })

    def get_test_results(self, time_to_recovery):
        '''After the delay in receiving test results, sets the
        `processing_results` boolean to `False`. Puts the node
        into quarantine if the test comes back positive.
        '''
        self.processing_results = False

        if(self.results):   # self.results and twin.results are the same, i think?
            self.node.quarantine(time_to_recovery)

    def set_parameters(self, args = None, cycles_per_day = 1):
        '''Update parameters via a dict argument `args`.
        '''
        # Hard-coded COVID-19 values
        if(args is None):
            self.cycles_per_day = cycles_per_day
            self.sensitivity = 0.8     # TP
            self.specificity = 0.98    # TN
            self.cost = 25
            self.results_delay = 0 * cycles_per_day
            self.rate = 0 * cycles_per_day

        else:
            for k, v, in args.items():
                if hasattr(self, k):
                    setattr(self, k, v)
            
            # Recalculate dependents
            keys = args.keys()

            # results delay
            if(any(key in keys for key in ['cycles_per_day', 'results_delay'])):
                self.results_delay = self.results_delay * cycles_per_day

            # rate
            if(any(key in keys for key in ['cycles_per_day', 'rate'])):
                self.rate = self.rate * cycles_per_day

    def take(self):
        '''Simulates a node taking a COVID test.
        Returns a boolean based on sensitivity/specificity parameters
        and whether or not the node is actually infected or not.
        '''
        # Increment the amount of tests this node has taken
        self.count += 1

        # Use positive rates for infected individuals
        if(self.node.state == 'infected asymptomatic'):
            if(self.rng.random() < self.sensitivity):
                self.results = True     # True positive
            else:
                self.results = False    # False negative

        # Use negative rates for susceptible/exposed/recovered individuals
        else:
            if(self.rng.random() < self.specificity):
                self.results = False    # True negative
            else:
                self.results = True     # False positive
                
        self.processing_results = True
        self.delay = 0 if self.results_delay == 0 else geometric_by_mean(self.rng, self.results_delay)

    def update(self, global_time, time_to_recovery):
        '''Runs once per cycle per node, updating its test information as follows:
        1. Waits for the test result's delay
            - Updates its node based on the results
        2. 
        '''
        # Copy params from previous time step
        twin = self.twin    # type: ignore
        twin.copy(self)

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
        bool_should_get_tested &=   (self.node.state != 'infected symptomatic'     # and   if node is not recovered/deceased/inf.symp. (those who already had infection will always test positive [FP])
                                    and self.node.state != 'recovered'
                                    and self.node.state != 'deceased')

        # Get tested if the above conditions pass
        if(bool_should_get_tested):
            self.take()

        # Receive test results Y days after being tested (if not quarantined)
        if(self.processing_results
        and self.delay == 0):
            self.get_test_results(time_to_recovery)

def geometric_by_mean(rng, mean, min = 0):
    # https://en.wikipedia.org/wiki/Geometric_distribution (mean = 1 / p)
    p = 1 / (mean - min)

    return(rng.geometric(p) + min)
