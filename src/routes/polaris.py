import logging
from enum import Enum

import networkx as nx
from meru.multilevel import MultiLevelModel

from routes.route_utils import path, vertex


# Define the weight of the edges
class Weight(Enum):
    TRAVEL_TIME = "traveltime"
    LENGTH = "length"


def polaris_paths(
    origin_destination_pairs: list[tuple[vertex, vertex]],
    G: nx.MultiDiGraph,
    weight: Weight,
) -> list[path]:
    meru_model = MultiLevelModel(G, k=3, attribute=weight.value)
    meru_model.parameter_selection(random_state=42)
    meru_model.fit(random_state=42)

    routes = []
    for origin, destination in origin_destination_pairs:
        output_paths = meru_model.predict(origin, destination)
        routes.append(output_paths)

    return routes
