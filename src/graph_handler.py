###
# File: graph_handler.py
# Created: 01/23/2021
# Author: Jordan Williams (jwilliams13@umassd.edu)
# -----
# Last Modified: 02/14/2021
# Modified By: Jordan Williams
###

"""
Reads a graph file (`*.adjlist`) from the configured directory according to parameters
if it exists, or generates and writes a new one if not.
"""

# Modules
import config
from log_handler import logging as log

# Packages
import networkx as nx
import numpy as np
import random
import re
import time
import timeit

g = []

def complete_graph(args):
    '''Connects each of n nodes to every other node.
    This raw function is much faster than using `nx.complete_graph(n).edges()`.
    Like, around 100 seconds faster (~120 to ~20) for n = 5000.
    '''
    # Unpack args
    n = args[0]

    g = nx.Graph()
    for j in range(n):
        for i in range(j + 1, n):
            g.add_edge(j, i)
    return(g)

def regular_graph(args):
    '''A graph where each vertex has the same number of neighbors;
    i.e. every vertex has the same degree or valency.
    https://en.wikipedia.org/wiki/Regular_graph
    '''
    # Unpack args
    n = args[0]
    k = args[1]

    regular_lattice = nx.Graph()
    for x in range(n):
        for y in range(k // 2): # FIXME(jordan): This will only give even-valued degrees
            regular_lattice.add_edge(x, (x + y + 1) % n)

    return(regular_lattice)

def wattsstrogatz_graph(args):
    '''Decent small-world model with low diameter and high clustering.
    https://en.wikipedia.org/wiki/Watts%E2%80%93Strogatz_model
    '''
    # Unpack args
    n = args[0]
    k = args[1]
    diameter_goal = args[2]
    rng = args[3]

    # Seed rng
    random.seed(rng)

    g = nx.Graph()
    # Keep track of what edges we will randomly choose from.
    # Start with a complete list of all possible edges.
    log.info("Watts-Strogatz generation requires a complete graph.")
    remaining_edges = import_graph('complete', [n])

    # Generate a regular lattice with n nodes, k neighbors
    log.info("Watts-Strogatz generation requires a regular graph.")
    regular_lattice = import_graph('regular', [n, k])

    # Remove the regular lattice edges from our complete set of remaining edges to choose from
    remaining_edges.remove_edges_from(regular_lattice.edges())
    remaining_edges = np.asarray(remaining_edges.edges()).tolist()

    # Clone the regular_lattice to a separate, independent graph g
    g = nx.compose(g, regular_lattice)
    regular_lattice = np.asarray(regular_lattice.edges()).tolist()

    # Initializations for edge count statistics
    edges_rewired_count = 0
    edges_total = len(regular_lattice)

    current_diameter = nx.diameter(g)
    edges_last_recalculation = 0
    # While the diameter is bigger than our goal...
    while current_diameter > diameter_goal:
        # Choose one random edge from our regular lattice to replace with one random edge from our list of remaining edges
        choice = random.choice(remaining_edges)
        edge_removed = random.choice(regular_lattice)

        # Replace the edge in our graph g
        g.remove_edge(edge_removed[0], edge_removed[1])
        g.add_edge(choice[0], choice[1])

        # Remove the randomly chosen edges from our lists so we don't pick them again
        regular_lattice.remove(edge_removed)
        remaining_edges.remove(choice)

        # Increment edges-rewired count
        edges_rewired_count += 1

        # Recalculate diameter only if % edges rewired changes by at least 1%.
        # TODO(jordan): Dynamically determine this value by the last calculated diameter?
        if((edges_rewired_count - edges_last_recalculation) / edges_total >= 0.01):
            current_diameter = nx.diameter(g)
            edges_last_recalculation = edges_rewired_count

            log.debug('Watts-Strogatz Graph Generation: %.2f%% (%d of %d: diameter = %d)' %
                    (100 * edges_rewired_count / edges_total, edges_rewired_count, edges_total, current_diameter))

    # Log statistics (how many edges needed to be rewired for this diameter, mCC)
    log.info('Watts-Strogatz Graph Generation: Took %.2f%% (%d of %d) of edges being rewired to reach a diameter of %d.' %
            (100 * edges_rewired_count / edges_total, edges_rewired_count, edges_total, diameter_goal))
    log.info('Watts-Strogatz Graph Generation: Mean clustering coefficient: %.4f.' % (nx.average_clustering(g)))

    return(g)

def build_file_name(graph_type = None, args = None, rng = None):
    '''Builds the file name to be either read or written for a graph file
    based on the graph type and arguments provided.
    '''
    # Read graph type from config as lowercase, stripping non-alphanumeric characters
    # (if no specific graph type is specified)
    if(graph_type is None):
        graph_type = re.sub(r'[\W_]+', '', config.settings['graph']['active']['type']).lower()

    # Ensure graph_type is valid (exists in graph definitions in config)
    try:
        graph_definition = config.settings['graph']['definitions'][graph_type]
    except Exception as e:
        log.error('Invalid graph type provided in config: not defined.')
        log.exception(e)
        raise e

    # Build graph args from config (if none are specified)
    if(args is None):
        args = config.settings['graph']['active']['properties']

    # Initialize name string with the graph_type
    name = graph_type

    # Iterate through each of the graph's properties and append its value
    # e.g.: "wattsstrogatz_n1500_k43_d3_rng0"
    for index, graph_property in enumerate(graph_definition['properties']):
        name += '_%s%d' % (graph_property['key'], args[index])

    # If graph has an element of randomness to it and a random seed is provided,
    # append the seed to be used
    if(rng is not None
    and graph_definition['random'].lower() == "true"):
        name += '_rng%d' % (rng)

    # Add the file extension defined in the config
    name += config.settings['graph']['extension']

    return(name)

def import_graph(graph_type = None, graph_args = None, rng = None, path = None):
    '''Reads a graph file (`*.adjlist`) from the configured directory according to parameters if it exists,
    or generates and writes a new one if not.
    '''

    if(path is None):
        # Read graph type from config as lowercase, stripping non-alphanumeric characters
        # (if no specific graph type is specified)
        if(graph_type is None):
            graph_type = re.sub(r'[\W_]+', '', config.settings['graph']['active']['type']).lower()

        # Ensure graph_type is valid (exists in graph definitions in config)
        try:
            graph_definition = config.settings['graph']['definitions'][graph_type]
        except Exception as e:
            log.error('Invalid graph type provided in config: not defined.')
            log.exception(e)
            raise e

        # If graph has an element of randomness and rng is not specified, generate a new seed
        if(graph_definition['random'].lower() == 'true'
            and rng is None):
            rng = int(1000 * time.time()) % 2**32

        # Build graph args from config (if none are specified)
        if(graph_args is None):
            graph_args = config.settings['graph']['active']['properties']
            
        # Build graph file name string
        file_name = build_file_name(graph_type, graph_args, rng)

        # Read from file if it exists
        path = './' + config.settings['graph']['directory'] + file_name
    try:
        log.info("Attempting to read graph from '%s'..." % (path))
        g = nx.read_adjlist(path, nodetype = int)
        log.info("Graph successfully read from '%s'..." % (path))
    except:
        log.info("Failed to read graph from '%s'. Generating..." % (path))

        # If graph has an element of randomness
        if(graph_definition['random'].lower()
            == 'true'):
            graph_args.append(rng)

        # Generate graph structure
        t0 = timeit.default_timer()
        try:
            g = eval('%s_graph(%s)' % (graph_type, graph_args))
        except Exception as e:
            log.exception('Graph generation failed.')
            log.exception(e)
            raise e
        t1 = timeit.default_timer()

        # Save graph to file
        nx.write_adjlist(g, path)
        log.info("Wrote new graph to '%s' (took %.6fs)." % (path, t1 - t0))

    # Return graph to caller function
    return(g)