import logging
import pickle
from enum import Enum

import igraph
import networkx as nx
from meru.multilevel import MultiLevelModel
from routing_lib import from_sumo_to_igraph_network
from slugify import slugify
from sumolib.net.edge import Edge
from tqdm import tqdm

import matsim_io
from config import ProgramConfig, set_amager_input_data, set_ravenna_input_data
from controller import controller_input_data, run_matsim
from data_loader.sumo import read_sumo_road_network
from main import save_analysis_files
from matsim_io.dashboards import (
    SimulationResult,
    append_breakpoints_to_congestion_map,
    change_departure_arrivals_bar_graph,
    change_population_visuals_map,
    copy_dashboard,
    create_comparison_dashboard,
)
from routes.fastest_path import FastestPath
from routes.route import create_route_objects
from routes.route_algo import RouteAlgo


class Weight(Enum):
    """Enum for the weight attribute used in the MultiLevelModel."""

    TRAVEL_TIME = "traveltime"
    LENGTH = "length"


def polaris_paths(
    edge_pairs: list[tuple[Edge, Edge]],
    graph: nx.MultiDiGraph,
    weight: Weight,
) -> list[list[dict[str, list[str] | list[int]]]]:
    model = MultiLevelModel(graph, k=3, attribute=weight.value)
    model.parameter_selection(n_vehicles=len(edge_pairs), random_state=42)
    model.fit(random_state=42)

    paths = []
    for from_edge, to_edge in tqdm(edge_pairs, desc="Predicting least popular paths"):
        paths.append(model.predict(from_edge, to_edge))

    return paths


def read_sumo_network_and_run_polaris(
    road_network_filename: str,
    conf: ProgramConfig,
    algorithm: RouteAlgo,
) -> tuple[
    igraph.Graph,
    list[list[dict[str, list[str] | list[int]]]],
    dict[str, int],
]:
    print("Reading SUMO network")
    net = read_sumo_road_network(road_network_filename)
    graph = from_sumo_to_igraph_network(net)

    output_name = slugify(algorithm.title)
    with open(f"{output_name}_igraph.pkl", "wb") as f:
        pickle.dump(graph, f)

    print("Computing routes")
    paths = algorithm.route_to_safety(conf.origin_points, conf.danger_zones, conf.G)
    with open(f"{output_name}_paths.pkl", "wb") as f:
        pickle.dump(paths, f)
    routes = create_route_objects(
        origin_to_paths=paths,
        population_data=conf.danger_zone_population_data,
        start=0,
        end=conf.departure_end_time_sec,
        cars_per_person=conf.cars_per_person,
    )
    stats = {
        "Amount of routes": len(routes),
        "Amount of nodes with no route to safety": len(conf.origin_points) - len(paths),
    }

    def first_outgoing_edge(node_id: str) -> Edge:
        node = net.getNode(str(node_id))
        edges = node.getOutgoing()
        return edges[0].getID()

    def last_incoming_edge(node_id: str) -> Edge:
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

    new_edge_pairs = [
        (from_edge, to_edge)
        for from_edge, to_edge in edge_pairs
        if from_edge and to_edge
    ]
    print(f"Routes with missing edges: {len(edge_pairs) - len(new_edge_pairs)}")

    print("Running Polaris")
    result_paths = polaris_paths(new_edge_pairs, graph, Weight.TRAVEL_TIME)

    print("Saving results")
    with open(f"{output_name}_polaris_paths.pkl", "wb") as f:
        pickle.dump(result_paths, f)

    return graph, result_paths, stats


if __name__ == "__main__":
    amager_input = set_amager_input_data()
    ravenna_input = set_ravenna_input_data()

    scenarios = [
        (FastestPath(), amager_input, "Amager - Polaris (1)", 1, "amager"),
        # (FastestPath(), amager_input, "Amager - Polaris (3)", 3, "amager"),
        (FastestPath(), ravenna_input, "Ravenna - Polaris (3)", 3, "ravenna"),
    ]

    results = []
    for algorithm, input_data, title, endpoints, city in scenarios:
        try:
            logging.info(f"Starting algorithm: {title}")
            conf = controller_input_data(input_data)
            conf.diversifying_routes = endpoints
            algorithm.title = title

            graph, paths, stats = read_sumo_network_and_run_polaris(
                f"{city}.net.xml.gz", conf, algorithm
            )
            matsim_io.write_polaris_network(graph)
            matsim_io.write_polaris_plans(paths)

            output_dir = slugify(f"{algorithm.title}-output")
            run_matsim(output_dir)
            save_analysis_files(conf, stats, output_dir)
            append_breakpoints_to_congestion_map(output_dir)
            change_population_visuals_map(
                output_dir, conf.danger_zone_population_data, conf.population_type
            )
            change_departure_arrivals_bar_graph(output_dir)
            copy_dashboard(output_dir, algorithm.title)

            results.append(SimulationResult(output_dir, algorithm.title))
        except Exception as e:
            logging.error(f"Error running algorithm {title}: {e}")

    create_comparison_dashboard(results)
