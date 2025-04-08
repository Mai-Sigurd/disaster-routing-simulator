import pickle
from enum import Enum

import networkx as nx
import sumolib.net.edge
from meru.multilevel import MultiLevelModel
from routing_lib import from_sumo_to_igraph_network
from tqdm import tqdm

from config import ONE_HOUR, TWO_MINUTES
from controller import controller_input_data, set_dev_input_data
from data_loader.sumo import read_sumo_road_network
from routes.route import create_route_objects
from routes.route_utils import path, vertex


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


if __name__ == "__main__":
    conf = controller_input_data(set_dev_input_data())
    paths = conf.route_algos[0].route_to_safety(
        conf.origin_points, conf.danger_zones, conf.G
    )
    routes = create_route_objects(
        list_of_paths=paths,
        population_data=conf.danger_zone_population_data,
        start=TWO_MINUTES,
        end=ONE_HOUR,
        cars_per_person=conf.cars_per_person,
    )

    net = read_sumo_road_network("copenhagen.net.xml.gz")
    G = from_sumo_to_igraph_network(net)

    def first_outgoing_edge(node_id: str) -> sumolib.net.edge.Edge:
        node = net.getNode(str(node_id))
        edges = node.getOutgoing()
        return edges[0].getID()

    def last_incoming_edge(node_id: str) -> sumolib.net.edge.Edge:
        node = net.getNode(str(node_id))
        edges = node.getIncoming()
        return edges[-1].getID()

    node_pairs = [
        (r.path[0], r.path[-1]) for r in routes for _ in range(r.num_people_on_route)
    ]
    edge_pairs = [
        (first_outgoing_edge(from_node), last_incoming_edge(to_node))
        for from_node, to_node in node_pairs
    ]

    model = MultiLevelModel(G, k=3, attribute=Weight.TRAVEL_TIME.value)
    model.parameter_selection(n_vehicles=len(edge_pairs), random_state=42)
    model.fit(random_state=42)

    result_paths = {}
    for from_edge, to_edge in tqdm(edge_pairs, desc="Predicting least popular paths"):
        result_paths[(from_edge, to_edge)] = model.predict(from_edge, to_edge)

    with open("copenhagen_igraph.pkl", "wb") as f:
        pickle.dump(G, f)
    with open("polaris_paths.pkl", "wb") as f:
        pickle.dump(result_paths, f)
