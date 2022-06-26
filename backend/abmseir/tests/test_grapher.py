###
# File: test_graph_handler.py
# Created: 03/24/2022
# Author: Jordan Williams (jwilliams4465@gmail.com)
# -----
# Last Modified: 06/02/2022
# Modified By: Jordan Williams
###

import functools
from typing import Callable

import networkx as nx
import numpy as np
import pytest
from abmseir import grapher

GRAPH_INPUT_ORDERS = [
    2,
    16,
    128,
    1024,
]


@pytest.mark.skip
@pytest.mark.parametrize("order", GRAPH_INPUT_ORDERS)
def test_graph_class(order: int):
    """Tests the Graph() class defined in `grapher.py`."""
    # __eq__
    graph_1 = grapher.Graph()
    graph_2 = grapher.Graph()

    for i in range(order):
        # Ensure edge is agnostic to node order
        graph_1.add_edge(-1, i)
        graph_2.add_edge(i, -1)

    assert graph_1 == graph_2  # type: ignore

    # __repr__
    graph_2.name = "Graph 2"
    assert type(graph_1.__repr__()) == str
    assert type(graph_2.__repr__()) == str


@pytest.mark.parametrize(
    "expected,order",
    [(nx.complete_graph(n=order), order) for order in GRAPH_INPUT_ORDERS],
)
def test_complete_graph(expected: nx.Graph, order: int):
    """Ensures that `grapher.complete_graph(order)` outputs a graph
    with properties consistent to the Complete Graph.

    https://en.wikipedia.org/wiki/Complete_graph
    """
    identifiers = {
        "order": order,
    }
    generator = functools.partial(grapher.complete_graph, **identifiers)

    edge_count = 0 if order <= 1 else order * (order - 1) / 2

    diameter = 0 if order <= 1 else 1

    _graph_validator(
        generator,
        expected,
        identifiers=identifiers,
        edge_count=edge_count,
        diameter=diameter,
    )


# TODO: add other jumps parameter types (set, list, range)
@pytest.mark.skip
@pytest.mark.parametrize(
    "expected,order,degree",
    [
        (
            nx.circulant_graph(n=order, offsets=range(1, (degree // 2) + 1)),
            order,
            degree,
        )
        for order in [4, 32, 256]
        for degree in [2, 8, 16]
        if degree < order and degree % 2 == 0
    ],
)
def test_circulant_graph_jump_int(expected: nx.Graph, order: int, degree: int):
    """Ensures that `grapher.circulant_graph(order, jumps)` outputs a graph with properties consistent to the Circulant Graph.

    https://en.wikipedia.org/wiki/Circulant_graph
    """
    identifiers = {
        "order": order,
        "jumps": set(range(1, (degree // 2) + 1, 1)),
    }
    generator = functools.partial(grapher.circulant_graph, **identifiers)

    edge_count = order * degree // 2

    diameter = 0 if degree % 2 == 1 else np.ceil(order / degree)

    _graph_validator(
        generator,
        expected,
        identifiers=identifiers,
        edge_count=edge_count,
        diameter=diameter,
    )


@pytest.mark.skip
@pytest.mark.parametrize(
    "order,degree,diameter,seed",
    [  # use every valid combination of these parameters
        (order, degree, diameter, seed)
        for order in [5000]  # 64, 256, 1024]
        for degree in [42]  # 4, 16, 64]
        for diameter in [3]  # 12, 6, 3]
        for seed in [None, 0, 5318008]
        if degree < order
        and degree % 2 == 0
        and diameter < order // 2
        and diameter < np.ceil(order / degree)
    ],
)
def test_modified_watts_strogatz_graph(
    order: int, degree: int, diameter: int, seed: int | None
):
    """Ensures that `grapher.modified_watts_strogatz_graph(order, degree, diameter, seed)` outputs a graph with properties consistent to the Watts-Strogatz model.

    https://en.wikipedia.org/wiki/Watts%E2%80%93Strogatz_model
    """
    identifiers = {
        "order": order,
        "degree": degree,
        "diameter": diameter,
        "seed": seed,
    }
    generator = functools.partial(grapher.modified_watts_strogatz_graph, **identifiers)

    edge_count = order * degree // 2

    _graph_validator(
        generator,
        identifiers=identifiers,
        edge_count=edge_count,
    )


def _graph_validator(generator: Callable, expected: nx.Graph | None = None, **kwargs):
    """Tests a graph's properties based on `order` and `**kwargs`."""
    graph = generator()

    # does our algorithm...
    # # generate the same graph as NetworkX's
    if expected:
        assert graph == expected

    # ensure graph object contains all required properties
    identifiers = kwargs.get("identifiers") or {}
    for key, value in graph.identifiers.items():
        assert key in identifiers.keys()
        assert value == identifiers.get(key)

    # # contain the correct number of nodes
    if "order" in identifiers.keys():
        assert graph.number_of_nodes() == identifiers.get("order")

    # # contain the correct number of edges
    if "edge_count" in kwargs.keys():
        assert graph.number_of_edges() == kwargs.get("edge_count")

    # # have the correct diameter
    if "diameter" in kwargs.keys():
        assert nx.diameter(graph) == kwargs.get("diameter")
