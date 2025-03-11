import logging
from enum import Enum

# import meru
# from meru.multilevel import MultiLevelModel
import networkx as nx

from routes.route_utils import path, vertex


# Define the weight of the edges
class Weight(Enum):
    traveltime = 1
    length = 2


def polaris_paths(
    origin_destination_pairs: list[tuple[vertex, vertex]],
    G: nx.MultiDiGraph,
    weight: Weight,
) -> list[path]:
    meru_model = MultiLevelModel(G, k=3, attribute=weight)
    meru_model.parameter_selection(random_state=42)

    routes = []
    for origin, destination in origin_destination_pairs:
        output_paths = meru_model.predict(origin, destination)
        routes.append(output_paths)

    return routes
