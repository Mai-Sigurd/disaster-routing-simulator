import pickle
from enum import Enum

import networkx as nx
from meru.multilevel import MultiLevelModel
from routing_lib import from_sumo_to_igraph_network
from sumolib.net.edge import Edge
from tqdm import tqdm

from config import set_amager_input_data, set_ravenna_input_data
from controller import controller_input_data
from data_loader.sumo import read_sumo_road_network
from routes.route import create_route_objects
from routes.route_utils import path, vertex


class Weight(Enum):
    """Enum for the weight attribute used in the MultiLevelModel."""

    TRAVEL_TIME = "traveltime"
    LENGTH = "length"


def polaris_paths(
    edge_pairs: list[tuple[Edge, Edge]],
    graph: nx.MultiDiGraph,
    weight: Weight,
) -> dict[tuple[vertex, vertex], path]:
    model = MultiLevelModel(graph, k=3, attribute=weight.value)
    model.parameter_selection(n_vehicles=len(edge_pairs), random_state=42)
    model.fit(random_state=42)

    paths = {}
    for from_edge, to_edge in tqdm(edge_pairs, desc="Predicting least popular paths"):
        paths[(from_edge, to_edge)] = model.predict(from_edge, to_edge)

    return paths


if __name__ == "__main__":
    scenarios = [
        ("copenhagen", set_amager_input_data()),
        ("ravenna", set_ravenna_input_data()),
    ]

    for city, input_data in scenarios:
        print(f"Running Polaris for {city.title()}")
        conf = controller_input_data(input_data)

        print("Reading SUMO network")
        net = read_sumo_road_network(f"{city}.net.xml.gz")
        graph = from_sumo_to_igraph_network(net)

        print("Computing routes")
        paths = conf.route_algos[0].route_to_safety(
            conf.origin_points, conf.danger_zones, conf.G
        )
        routes = create_route_objects(
            list_of_paths=paths,
            population_data=conf.danger_zone_population_data,
            start=0,
            end=conf.departure_end_time_sec,
            cars_per_person=conf.cars_per_person,
        )

        def first_outgoing_edge(node_id: str) -> Edge:
            node = net.getNode(str(node_id))
            edges = node.getOutgoing()
            return edges[0].getID()

        def last_incoming_edge(node_id: str) -> Edge:
            node = net.getNode(str(node_id))
            edges = node.getIncoming()
            return edges[-1].getID()

        node_pairs = [
            (r.path[0], r.path[-1])
            for r in routes
            for _ in range(r.num_people_on_route)
        ]
        edge_pairs = [
            (first_outgoing_edge(from_node), last_incoming_edge(to_node))
            for from_node, to_node in node_pairs
        ]

        print("Running Polaris")
        result_paths = polaris_paths(edge_pairs, graph, Weight.TRAVEL_TIME)

        print("Saving results")
        with open(f"{city}_igraph.pkl", "wb") as f:
            pickle.dump(graph, f)
        with open(f"{city}_polaris_paths.pkl", "wb") as f:
            pickle.dump(result_paths, f)
