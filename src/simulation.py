###
# File: simulation.py
# Created: 01/25/2021
# Author: Jordan Williams (jwilliams13@umassd.edu)
# -----
# Last Modified: 04/20/2021
# Modified By: Jordan Williams
###

"""
Simulates the infectious spread across a community (graph) based on parameters defined in config.json.
"""

# Modules
from log_handler import logging as log

# Packages
import datetime
import math
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
        self.data_states = ['test count', 'true positive', 'false positive', 'new false positive'
            , 'returning false positive', 'exogenous', 'generation 1', 'generation 2', 'generation 3'
            , 'generation 4', 'generation 5', 'generation x', 'interactions', 'infected nodes'
            , 'susceptibles contracting'
        ]
        
        # Simulation constants
        # TODO(jordan): Log this seed
        self.rng = np.random.default_rng()  # type: ignore
        self.graph = g
        self.old_index, self.new_index = 0, 1
        self.nodes = [[], []]       # type: List[List[Node]]
        self.nodes[self.old_index] = self.generate_nodes()
        self.nodes[self.new_index] = self.generate_nodes()
        self.previous_infected_nodes = self.current_infected_nodes = set() # type: Set[int]

        # Simulation parameters
        self.set_parameters()

        # Simulation data
        self.data = self.generate_data_container()
        self.time_index = 0

    def add_exposed_cases(self, amount, exogenous = None, node_index = None):
        '''Sets a number of cases specified by `amount` to exposed.
        This represents cases coming onto campus from outside sources,
        e.g. an individual getting infected while visiting home.
        '''
        if(node_index is None):
            node_index = self.new_index
        nodes = self.nodes[node_index]

        # Susceptible, non-quarantined nodes
        susceptible_nodes = [node.index for node in nodes if (node.state == 'susceptible' and node.quarantine_time == 0)]
        
        # If there aren't enough susceptible nodes remaining to expose,
        # just expose the rest.
        if(len(susceptible_nodes) <= amount):
            chosen_indices = susceptible_nodes
        else:   # Otherwise, randomly choose an `amount` of susceptible nodes to expose.
            # The `replace` parameter ensures we don't choose duplicates.
            chosen_indices = self.rng.choice(susceptible_nodes, amount, replace = False)

        # Expose these nodes
        for i in chosen_indices:
            nodes[i].get_exposed()
            if(exogenous is not None):
                nodes[i].exogenous = exogenous

    def add_infected_cases(self, amount, node_index = None, generation = 1):
        '''Sets a number of cases specified by `amount` to infected.
        '''
        if(node_index is None):
            node_index = self.new_index
        nodes = self.nodes[node_index]

        # Susceptible, non-quarantined nodes
        susceptible_nodes = [node.index for node in nodes if (node.state == 'susceptible' and node.quarantine_time == 0)]
        
        # If there aren't enough susceptible nodes remaining to infect,
        # just infect the rest.
        if(len(susceptible_nodes) <= amount):
            chosen_indices = susceptible_nodes
        else:   # Otherwise, randomly choose an `amount` of susceptible nodes to infect.
            # The `replace` parameter ensures we don't choose duplicates.
            chosen_indices = self.rng.choice(susceptible_nodes, amount, replace = False)

        # Infect these nodes
        for i in chosen_indices:
            nodes[i].get_infected(self.current_infected_nodes)
            nodes[i].generation = generation

    def add_recovered_cases(self, amount, node_index = None):
        '''Sets a number of cases specified by `amount` to recovered.
        '''
        if(node_index is None):
            node_index = self.new_index
        nodes = self.nodes[node_index]

        # Susceptible, non-quarantined nodes
        susceptible_nodes = [node.index for node in nodes if (node.state == 'susceptible' and node.quarantine_time == 0)]
        
        # If there aren't enough susceptible nodes remaining to be recovered,
        # just recover the rest.
        if(len(susceptible_nodes) <= amount):
            chosen_indices = susceptible_nodes
        else:   # Otherwise, randomly choose an `amount` of susceptible nodes to recover.
            # The `replace` parameter ensures we don't choose duplicates.
            chosen_indices = self.rng.choice(susceptible_nodes, amount, replace = False)

        # Recover these nodes
        for i in chosen_indices:
            nodes[i].get_recovered()

    def calculate_r0(self):
        cols = ['generation 1', 'generation 2', 'generation 3', 'generation 4'
            , 'generation 5', 'generation x']
        # R0 calculating
        df = self.data[cols].iloc[-1]

        # Return R0
        return(df)

    def count_states(self, t):
        nodes = self.nodes[self.new_index]
        # Count data structure
        data_per_state = {}
        for state in self.all_states:
            data_per_state[state] = 0
        data_per_state['cycle'] = int(t)

        # Extra stats to track
        for state in self.data_states:
            data_per_state[state] = int(0)

        # Daily counts
        for node in nodes:
            data_per_state[node.state] += 1

            # Count how many tests have been taken up to this point
            data_per_state['test count'] += node.test.count

            # Count how many TP/FP tests in this state
            if(node.quarantine_time > 0):
                if(node.state == 'susceptible'):   # NOTE(jordan): Currently, exposed cases are FPs
                    data_per_state['false positive'] += 1
                    if(node.new_false_positive):
                        data_per_state['new false positive'] += 1
                elif(node.state == 'infected asymptomatic'):
                    data_per_state['true positive'] += 1

            elif(node.returning_false_positive):
                data_per_state['returning false positive'] += 1

            # Count states regarding exogenous
            if(node.exogenous >= 0):
                data_per_state['exogenous'] += 1

            # Infection generations
            else:
                if(node.generation == 0):
                    pass
                elif(node.generation == 1):
                    data_per_state['generation 1'] += 1
                elif(node.generation == 2):
                    data_per_state['generation 2'] += 1
                elif(node.generation == 3):
                    data_per_state['generation 3'] += 1
                elif(node.generation == 4):
                    data_per_state['generation 4'] += 1
                elif(node.generation == 5):
                    data_per_state['generation 5'] += 1
                else:
                    data_per_state['generation x'] += 1

            #if(node.state == 'infected asymptomatic'):
            #    self.confirming_PIV.add(node.index)
            data_per_state['interactions'] = self.total_interactions[0]

            data_per_state['infected nodes'] = len(self.previous_infected_nodes)
            data_per_state['susceptibles contracting'] = self.total_interactions[1]

        self.susceptible_count = data_per_state['susceptible']

        # Save data
        self.data = self.data.append(data_per_state, ignore_index = True)
    
    def export_data(self):
        return(self.data.to_csv(line_terminator = '\n'))

    def generate_data_container(self):
        cols = ['cycle']
        cols.extend(self.all_states)
        cols.extend(self.data_states)

        data = pd.DataFrame(dtype = int, columns = cols)
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
            'initial_cases': self.initial_cases,

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
        old_nodes = self.nodes[self.old_index]
        self.susceptible_count = n = self.population_size - self.initial_cases['infected asymptomatic']

        # Allocate which nodes will test on which days
        rate = old_nodes[0].test.rate
        if(rate != 0):
            test_group_size = math.ceil(n / rate)  # TODO(jordan): This doesn't feel correct
            for i in range(rate):
                if((i + 1) * test_group_size <= n):
                    bound = (i + 1) * test_group_size
                else:
                    bound = -1

                for node in old_nodes[i * test_group_size : bound]:
                    node.test.testing_delay = rate - i

        # Set initial case states (e.g., add 10 infected asymptomatic nodes)
        self.add_exposed_cases(self.initial_cases['exposed'], 0, self.old_index)
        self.add_infected_cases(self.initial_cases['infected asymptomatic'], self.old_index)
        self.add_recovered_cases(self.initial_cases['recovered'], self.old_index)

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
        time_index_wrapped = self.time_index + 1
        if(time_index_wrapped % self.exogenous_frequency == 0
        and time_index_wrapped != 1):
            self.add_exposed_cases(self.exogenous_amount, self.time_index)

        # Update list of infected nodes
        self.previous_infected_nodes = self.current_infected_nodes.copy()

        self.total_interactions = [0, 0]

        # Update each node
        old_nodes, new_nodes = self.nodes[self.old_index], self.nodes[self.new_index]
        for node in new_nodes:
            node.update(self.time_index, old_nodes, [self.previous_infected_nodes, self.current_infected_nodes], self.total_interactions)

        # Spread from each of previous_infected_nodes
        for node in [old_nodes[infected_index] for infected_index in self.previous_infected_nodes]:
            node.spread([old_nodes, new_nodes], self.susceptible_count, self.total_interactions)

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
            self.initial_cases = {
                'exposed': 0,
                'infected asymptomatic': 1,
                'recovered': 0
            }

            self.cycles_per_day = 3
            self.time_horizon   = 80 * self.cycles_per_day

            self.exogenous_amount       = 0
            self.exogenous_frequency    = 7 * self.cycles_per_day

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

        # Calculate effective number of neighbors each node will interact with each cycle
        active_neighbor_count = int(np.ceil(self.r0 + 10))  # type: ignore
        '''
        active_neighbor_count = self.population_size
        for initial_case, value in self.initial_cases.__dict__.items():
            active_neighbor_count -= value
            '''

        # If mean_node_degree is smaller than active_neighbor_count, use it instead
        active_neighbor_count = min(active_neighbor_count, mean_node_degree)

        # Pass params to nodes.
        for node in (nodes or self.nodes[self.old_index] + self.nodes[self.new_index]):
            node.set_parameters(args, self.cycles_per_day, self.r0, active_neighbor_count)

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
        #self.state_time = 0

        self.new_false_positive = False
        self.returning_false_positive = False

    def spread(self, nodes, susceptible_count, total_interactions):
        '''Spreads infection with some probability `transmission_rate`
        from neighboring, non-quarantined Nodes.
        '''
        old_nodes = nodes[0]    # type: list[Node]
        new_nodes = nodes[1]    # type: list[Node]

        # If we are quarantined, we can't spread the virus
        if(self.quarantine_time > 0):
            return

        # States that are considered interactible with
        valid_states = ["susceptible", "exposed", "infected asymptomatic", "recovered"]

        # Generate new random set of active neighbors
        # Interactible, non-quarantined nodes
        nodes_to_spread_to = [index for index in self.neighbors if (
            old_nodes[index].state in valid_states
            and old_nodes[index].quarantine_time == 0
            #and new_nodes[index].state in valid_states  # TODO(jordan): This determines whether or not overlap occurs from other infectives
        )]

        # Randomly choose an `active_neighbor_count` of infectible nodes to interact with,
        # if we still have enough
        if(len(nodes_to_spread_to) > self.active_neighbor_count):
            nodes_to_spread_to = self.rng.choice(nodes_to_spread_to, self.active_neighbor_count, replace = False)   # type: list[int]

        # Grab infected neighbors
        total_interactions[0] += min(self.active_neighbor_count, len(nodes_to_spread_to))
        total_interactions[1] += 1

        # Update transmission rate (dynamic)
        #self.transmission_rate = 0 if susceptible_count == 0 else self.beta / susceptible_count

        # Iterate through the next time step's chosen nodes
        for neighbor in [new_nodes[index] for index in nodes_to_spread_to]:

            # Spread to this neighbor if the random chance succeeds...
            if( neighbor.state == 'susceptible'
            and self.rng.random() < self.transmission_rate):
                # Expose it
                neighbor.get_exposed(self.generation + 1)

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
            dest.exogenous          = self.exogenous
            dest.generation         = self.generation
            dest.quarantine_time    = self.quarantine_time
            dest.state              = self.state
            #dest.state_time         = self.state_time
            
            dest.new_false_positive         = False #self.new_false_positive
            dest.returning_false_positive   = False #self.returning_false_positive

            # Also copy Test params
            self.test.copy(dest.test)

    def get_exposed(self, generation = None):
        assert self.state == 'susceptible'
        # Get exposed
        self.state = 'exposed'            
        #self.state_time = geometric_by_mean(self.rng, self.time_to_infection_mean, self.time_to_infection_min)

        if(generation is not None):
            # Track which generation this is
            self.generation = generation

    def get_infected(self, current_infected_nodes):
        self.state = 'infected asymptomatic'

        # Pull from geometric distribution with mean = `time_to_recovery`
        #self.state_time = geometric_by_mean(self.rng, self.time_to_recovery_mean)#, self.time_to_recovery_min)

        # Add self to list of `current_infected_nodes`
        current_infected_nodes.add(self.index)

    def get_parameters(self, all = False):
        params = {
            'cycles_per_day': self.cycles_per_day,
            'r0': self.r0,

            'time_to_infection_mean': self.time_to_infection_mean,
            'time_to_infection_min': self.time_to_infection_min,
            'incubation_rate': self.incubation_rate,

            'time_to_recovery_mean': self.time_to_recovery_mean,
            'time_to_recovery_min': self.time_to_recovery_min,
            'recovery_rate': self.recovery_rate,

            'symptoms_probability': self.symptoms_probability,
            'symptoms_rate': self.symptoms_rate,

            'death_probability': self.death_probability,
            'death_rate': self.death_rate,

            'beta': self.beta,
            'active_neighbor_count': self.active_neighbor_count,
            'transmission_rate': self.transmission_rate
        }
        if(all):
            # Put params into one dict
            params.update(self.test.get_parameters())
        
        return(params)

    def get_recovered(self, current_infected_nodes = None):
        # Get recovered
        self.state = 'recovered'
        if(current_infected_nodes is not None):
            self.get_uninfected(current_infected_nodes)

    def get_symptoms(self, current_infected_nodes):
        # Get symptoms
        self.state = 'infected symptomatic'
        self.get_uninfected(current_infected_nodes)

    def get_uninfected(self, current_infected_nodes):
        # Remove self from list of `current_infected_nodes`
        try:
            current_infected_nodes.remove(self.index)
        except KeyError:
            pass

    def quarantine(self, time_to_recovery_mean = 14):
        '''If a node receives a positive test result, they will quarantine
        for a mean time of `14` (geometric distribution).
        '''
        # 14 days flat
        self.quarantine_time = 1 #time_to_recovery_mean

        if(self.state == 'susceptible'):
            self.new_false_positive = True

    def set_neighbors(self, neighbor_indices):
        self.neighbors = neighbor_indices

    def set_parameters(self, args = None, cycles_per_day = 1, r0 = None, active_neighbor_count = None):
        '''Update parameters via a dict argument `args`.
        '''
        # Hard-coded COVID-19 values
        if(args is None):
            self.cycles_per_day = cycles_per_day
            self.r0 = r0

            # i.e. incubation time
            self.time_to_infection_mean = 3 * cycles_per_day
            self.time_to_infection_min = 0 * cycles_per_day
            self.incubation_rate = 1 / self.time_to_infection_mean

            self.time_to_recovery_mean = 14 * cycles_per_day
            self.time_to_recovery_min = 0 * cycles_per_day
            self.recovery_rate = 1 / self.time_to_recovery_mean

            self.symptoms_probability = 0#.30
            symptoms_ratio = self.symptoms_probability / (1 - self.symptoms_probability)
            self.symptoms_rate = symptoms_ratio / self.time_to_recovery_mean

            self.death_probability = 0#.0005
            death_ratio = self.death_probability / (1 - self.death_probability)
            self.death_rate = death_ratio / self.time_to_recovery_mean

            self.beta = r0 * (self.recovery_rate + self.symptoms_rate)
            self.active_neighbor_count = active_neighbor_count
            self.transmission_rate = self.beta / self.active_neighbor_count

        else:
            # Update attribute if it already exists in Node class
            for k, v, in args.items():
                if hasattr(self, k):
                    self.__dict__.update((k, v))
            
            # Recalculate dependents
            keys = args.keys()

            # incubation rate
            if(any(key in keys for key in ['cycles_per_day', 'time_to_infection_mean', 'time_to_infection_min'])):
                self.time_to_infection_mean = self.time_to_infection_mean * cycles_per_day
                self.time_to_infection_min = self.time_to_infection_min * cycles_per_day
                self.incubation_rate = 1 / self.time_to_infection_mean

            # recovery rate
            if(any(key in keys for key in ['cycles_per_day', 'time_to_recovery_mean', 'time_to_recovery_min'])):
                self.time_to_recovery_mean = self.time_to_recovery_mean * cycles_per_day
                self.time_to_recovery_min = self.time_to_recovery_min * cycles_per_day
                self.recovery_rate = 1 / self.time_to_recovery_mean

            # symptoms rate
            if(any(key in keys for key in ['cycles_per_day', 'time_to_recovery_mean', 'time_to_recovery_min', 'symptoms_probability'])):
                self.symptoms_rate = (self.symptoms_probability / (1 - self.symptoms_probability)) / self.time_to_recovery_mean

            # death rate
            if(any(key in keys for key in ['cycles_per_day', 'time_to_recovery_mean', 'time_to_recovery_min', 'death_probability'])):
                self.death_rate = (self.death_probability / (1 - self.death_probability)) / self.time_to_recovery_mean

            # transmission rate
            if(any(key in keys for key in ['cycles_per_day', 'time_to_recovery_mean', 'time_to_recovery_min', 'symptoms_probability', 'r0', 'active_neighbor_count'])):
                self.beta = r0 * ((1 / self.time_to_recovery_mean) + self.symptoms_rate)
                self.active_neighbor_count = active_neighbor_count
                self.transmission_rate = self.beta / active_neighbor_count

        # Pass params to corresponding Test object
        self.test.set_parameters(args, cycles_per_day)

    def update(self, global_time, nodes, infected_nodes, total_interactions):
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
        #if(self.state_time > 0):
        #    self.state_time -= 1
        
        # Generate random value [0, 1) to use
        rng = self.rng.random()

        # susceptible
        if(self.state == 'susceptible'):
            # In quarantine
            if(self.quarantine_time > 0):
                # Chance of leaving quarantine
                if(rng < self.recovery_rate):
                    self.quarantine_time -= 1
                    self.returning_false_positive = True

            # Not quarantined
            else:
                # If we have been marked as an exogenous case, gain infection
                if(self.exogenous >= 0):
                    self.get_exposed()

                # Otherwise, contract infection with some probability from neighbors
                else:
                    #self.contract(nodes, previous_infected_nodes, total_interactions)
                    pass

        # exposed
        elif(self.state == 'exposed'):
            # Progress from exposed to infected state after mean incubation period (3 days)
            if(rng < self.incubation_rate):
                self.get_infected(current_infected_nodes)

        # infected asymptomatic
        elif(self.state == 'infected asymptomatic'):
            # Progress from infected to recovered state after mean recovery time (14 days)

            # Recover at some rate
            if(rng < self.recovery_rate):
                if(self.quarantine_time > 0):
                    self.quarantine_time -= 1
                self.get_recovered(current_infected_nodes)

            # Gain symptoms with some probability (0.30) at some rate
            elif(rng < self.symptoms_rate + self.recovery_rate):
                if(self.quarantine_time > 0):
                    self.quarantine_time -= 1
                self.get_symptoms(current_infected_nodes)

        # infected symptomatic
        elif(self.state == 'infected symptomatic'):
            # Progress from infected to recovered state after mean recovery time (14 days)
            
            if(rng < self.recovery_rate):
                self.state = 'recovered'

            # Die with some probability (0.0005) at some rate
            elif(rng < self.death_rate + self.recovery_rate):
                self.state = 'deceased'

        # recovered/deceased
        else:
            #elif(self.state == 'recovered'
            #or  self.state == 'deceased'):
            pass

        # NOTE(jordan): Trying out test.update() after node.update() stuff, instead of before
        # Update test properties
        self.test.update(global_time, self.time_to_recovery_mean)

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
            dest.count          = self.count
            dest.results        = self.results
            dest.delay          = self.delay
            dest.testing_delay  = self.testing_delay
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

        if(self.results):
            ttr = 0
            # If false positive (Susceptible), pull quarantine time from distribution like Paltiel
            if(self.node.state in ['susceptible', 'exposed']):
                ttr = geometric_by_mean(self.rng, time_to_recovery)
            # If true positive (Infected asymptomatic), set quarantine time to rest of recovery time
            else:
                pass
                #ttr = self.node.state_time

            self.node.quarantine()#ttr)

    def set_parameters(self, args = None, cycles_per_day = 1):
        '''Update parameters via a dict argument `args`.
        '''
        # Hard-coded COVID-19 values
        if(args is None):
            self.cycles_per_day = cycles_per_day
            self.sensitivity = 0 #1 #0.8     # TP
            self.specificity = 1 #0.98    # TN
            self.cost = 25
            #self.results_delay = 0 * cycles_per_day    # TODO(jordan): Revert this to 1 or 2 days
            self.results_delay = 1

            # Limit these granularity to daily
            self.rate = 0#14 * cycles_per_day
            self.testing_delay = self.rate

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

    def take(self):
        '''Simulates a node taking a COVID test.
        Returns a boolean based on sensitivity/specificity parameters
        and whether or not the node is actually infected or not.
        '''
        # Increment the amount of tests this node has taken
        self.count += 1

        # Generate random value [0, 1) to use
        rng = self.rng.random()

        # Use positive rates for infected individuals
        if(self.node.state == 'infected asymptomatic'):
            if(rng < self.sensitivity):
                self.results = True     # True positive
            else:
                self.results = False    # False negative

        # Use negative rates for susceptible/exposed individuals
        else:
            if(rng < self.specificity):
                self.results = False    # True negative
            else:
                self.results = True     # False positive

        if(self.node.state != 'infected asymptomatic' and
        self.node.state != 'susceptible'):
            print('Bad state: %s' % (self.node.state))

        self.processing_results = True
        self.delay = 0 if self.results_delay == 0 else geometric_by_mean(self.rng, self.results_delay)
        
    def update(self, global_time, time_to_recovery):
        '''Runs once per cycle per node, updating its test information as follows:
        1. Waits for the test result's delay
            - Updates its node based on the results
        '''
        # Copy params from previous time step
        self.twin.copy(self)    # type:ignore

        # Decrement and wrap testing_delay (limit granularity to once per day)
        #bool_day_granularity = global_time % self.cycles_per_day == 0
        if(self.rate != 0):# and bool_day_granularity):
            self.testing_delay = (self.testing_delay - 1) % self.rate

        # If we are waiting on the latest test results, decrement the delay we are waiting
        if(self.processing_results):
            self.delay -= 1

        # Determine if we should get tested
                                                                        # Only test if:
        bool_should_get_tested  =   self.rate != 0                      #       `self.rate` is not 0
        bool_should_get_tested &=   self.testing_delay == 0             # and   if we are scheduled to test today
        #bool_should_get_tested &=   bool_day_granularity                # and   if we limit granularity to once per day
        bool_should_get_tested &=   self.node.quarantine_time == 0      # and   if we aren't already in quarantine
        bool_should_get_tested &=   not self.processing_results         # and   if we aren't already waiting on our last test]
        # TODO(jordan): this will prevent high test rates (e.g. 1 day). Need to remake this to have a list of results coming in with their individual delays
        bool_should_get_tested &=   (self.node.state == 'infected asymptomatic'     # and   if node is not recovered/deceased/inf.symp. (those who already had infection will always test positive [FP])
                                    or self.node.state == 'susceptible'
                                    #and self.node.state != 'exposed'    # TODO(jordan): Technically, Paltiel is not testing Exposed individuals
                                    )

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
