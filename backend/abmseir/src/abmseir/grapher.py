###
# File: graph_handler.py
# Created: 01/23/2021
# Author: Jordan Williams (theafroofdoom@gmail.com)
# -----
# Last Modified: 06/07/2022
# Modified By: Jordan Williams
###

"""
Reads a graph file (`*.adjlist`) from the configured directory according to parameters
if it exists, or generates and writes a new one if not.
"""

import json
import random
from functools import wraps
from typing import Callable, Union

import networkx as nx
import numpy as np

from abmseir.log_handler import logging as log


# TODO: remove this once logging is fixed
class Temp:  # pylint: disable=missing-class-docstring
    def __init__(self):
        self.info = self.exception = self.debug = self.error = print


log = Temp()


class Graph(nx.Graph):
    """Extends the :class:`~networkx.Graph` class with the following:
    * basic equality comparison
    * better string representation
    * a function to convert the graph to an adjacency list as binary data
    """

    def __init__(self, **kwargs):
        self.identifiers = kwargs
        super().__init__()

    def __eq__(self, other: nx.Graph):
        return self.nodes, self.edges == other.nodes, other.edges

    def __repr__(self):
        return (
            "".join(
                [
                    f"{type(self).__name__}(",
                    "".join(
                        [f"{key}={value}," for key, value in self.identifiers.items()]
                    ),
                    f"name='{self.name!r}'," if self.name else "",
                ]
            )
            + ")"
        )

    def __str__(self):
        return self.__repr__()

    def to_binary(self):
        """Converts the graph into an adjacency list file format
        (:func:`~networkx.generate_adjlist`) and encodes it into ASCII data.
        """
        # return "\n".join(list(nx.generate_adjlist(self))).encode("ascii")
        return json.dumps(nx.cytoscape_data(self)).encode("ascii")


def randomizable(generator: Callable):
    """Decorator that initializes a graph's `seed` parameter if it is not provided. Should be"""

    @wraps(generator)
    def randomize_seed(*_, **kwargs):
        if kwargs["seed"] is None:
            kwargs["seed"] = np.random.randint(-(2**31), 2**31 - 1)

    # Return graph to caller function
    return randomize_seed


def complete_graph(order: int) -> Graph:
    """Connects each of `order` nodes to every other node.
    This raw function is much faster than using `nx.complete_graph(n).edges()`.
    Like, around 100 seconds faster (~120s to ~20s) for n = 5000.
    (https://en.wikipedia.org/wiki/Complete_graph)
    """

    graph = Graph(order=order)

    for i in range(order - 1):
        for j in range(i + 1, order):
            graph.add_edge(i, j)
    return graph


# def circulant_graph(order: int, jumps: range | set[int] | list[int] | int) -> Graph: # python 3.10
def circulant_graph(order: int, jumps: Union[range, set[int], list[int], int]) -> Graph:
    """A graph where each vertex has the same number of neighbors;
    i.e. every vertex has the same degree or valency.
    (https://en.wikipedia.org/wiki/Circulant_graph)
    """

    if isinstance(jumps, int):
        jumps = range(1, jumps + 1, 1)
    elif isinstance(jumps, list):
        jumps = set(jumps)

    graph = Graph(order=order, jumps=set(jumps))
    # TODO: This can likely be optimized to not add duplicate edges by only
    # going up to a certain node index depending on the highest jump value
    graph.add_edges_from(
        set(
            [
                (node, to(node, jump))
                for node in range(order)
                for jump in jumps
                for to in (
                    lambda node, jump: (node + jump) % order,
                    lambda node, jump: (node - jump) % order,
                )
            ]
        )
    )
    # assert 0

    return graph


# TODO: Add optional graph arguments (complete, circulant) for function to use
# instead of creating new ones
# TODO: Save any generated complete/circulant graphs if they are not provided
@randomizable
def modified_watts_strogatz_graph(
    # order: int, degree: int, diameter: int, seed: int | None = None # python 3.10
    order: int,
    degree: int,
    diameter: int,
    seed: Union[int, None] = None,
) -> Graph:
    """Decent small-world model with low diameter and high clustering.
    (https://en.wikipedia.org/wiki/Watts%E2%80%93Strogatz_model)
    """
    # Seed rng
    random.seed(seed)

    # Keep track of what edges we will randomly choose from.
    # Start with a complete list of all possible edges.
    log.info("Watts-Strogatz generation requires a complete graph.")
    new_edges = complete_graph(order)

    # Generate a circulant graph with `order` nodes, `degree` neighbors
    log.info("Watts-Strogatz generation requires a circulant graph.")
    circulant = circulant_graph(order, degree // 2)

    # Remove the circulant graph edges from our complete set of remaining edges to choose from
    new_edges.remove_edges_from(circulant.edges())
    new_edges = np.asarray(new_edges.edges()).tolist()  # type: ignore

    # Clone the circulant_graph to a separate, independent graph graph
    graph = nx.compose(Graph(), circulant)  # type: Graph

    # Remove bridges so graph cannot become disconnected
    replaceable_edges = circulant
    replaceable_edges.remove_edges_from(nx.bridges(replaceable_edges))

    # Initializations for edge count statistics
    edges_rewired_count = 0
    edges_total = len(circulant)

    current_diameter = nx.diameter(graph)
    edges_last_recalculation = 0

    # While the current diameter of the graph is bigger than our goal...
    while current_diameter > diameter:  # type: ignore
        # Choose one random edge from our replaceable_edges to replace with one
        # random edge from our list of remaining edges
        choice = random.choice(new_edges)
        edge_removed = random.choice(list(replaceable_edges.edges()))

        # Replace the edge in our watts-strogatz graph
        graph.remove_edge(*edge_removed)
        graph.add_edge(choice[0], choice[1])

        # Remove the randomly chosen edges from our lists so we don't pick them again
        replaceable_edges.remove_edge(*edge_removed)
        new_edges.remove(choice)

        # Increment edges-rewired count
        edges_rewired_count += 1

        # Remove bridges
        replaceable_edges.remove_edges_from(nx.bridges(replaceable_edges))

        # Recalculate diameter only if % edges rewired changes by at least 1%.
        # TODO: Dynamically determine this value by the last calculated diameter?
        # TODO: Calculate min edges before next check using `0.01 * edges_total`
        if (edges_rewired_count - edges_last_recalculation) / edges_total >= 0.01:
            current_diameter = nx.diameter(graph)
            edges_last_recalculation = edges_rewired_count

            percent_edges_rewired = 100 * edges_rewired_count / edges_total
            log.debug(
                "".join(
                    [
                        "Watts-Strogatz Graph Generation:"
                        f" {percent_edges_rewired:.2f}% ",
                        f"({edges_rewired_count} of {edges_total}: ",
                        f"diameter = {current_diameter})",
                    ]
                )
            )

    # Log statistics (how many edges needed to be rewired for this diameter, mCC)
    log.info(
        "".join(
            [
                "Watts-Strogatz Graph Generation: ",
                f"Took {100 * edges_rewired_count / edges_total:.2f}% ",
                f"({edges_rewired_count} of {edges_total}) ",
                f"of edges being rewired to reach a diameter of {diameter}",
            ]
        )
    )
    log.info(
        "Watts-Strogatz Graph Generation: Mean clustering coefficient:"
        f" {nx.average_clustering(graph):.4f}."
    )

    return graph
