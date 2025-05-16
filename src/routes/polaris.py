import logging
import pickle
import random
import traceback
from collections import defaultdict
from enum import Enum

import igraph
import networkx as nx
from meru.multilevel import MultiLevelModel
from routing_lib import from_sumo_to_igraph_network
from slugify import slugify
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
from routes.route import _get_normal_dist_departure_time_list, create_route_objects
from routes.route_algo import RouteAlgo


class Weight(Enum):
    """Enum for the weight attribute used in the MultiLevelModel."""

    TRAVEL_TIME = "traveltime"
    LENGTH = "length"


def polaris_paths(
    edge_pairs: list[tuple[str, str, int]],
    graph: nx.MultiDiGraph,
    weight: Weight,
) -> list[list[dict[str, list[str] | list[int]]]]:
    model = MultiLevelModel(graph, k=3, attribute=weight.value)
    model.parameter_selection(
        n_vehicles=sum(k for _, _, k in edge_pairs), random_state=42
    )
    model.fit(random_state=42)

    paths = []
    for from_e, to_e, k in tqdm(edge_pairs, desc="Predicting least popular paths"):
        paths.append(model.predict(from_e, to_e, k))

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
    paths = algorithm.route_to_safety(
        conf.origin_points, conf.danger_zones, conf.G, conf.diversifying_routes
    )
    with open(f"{output_name}_paths.pkl", "wb") as f:
        pickle.dump(paths, f)
    routes = create_route_objects(
        origin_to_paths=paths,
        population_data=conf.danger_zone_population_data,
        start=0,
        end=conf.departure_end_time_sec,
        cars_per_person=conf.cars_per_person,
    )

    def outgoing_edge(node_id: str) -> str:
        for edge in net.getNode(str(node_id)).getOutgoing():
            if _is_driveable(edge.getType()):
                return str(edge.getID())
        raise ValueError(f"No outgoing edge found for node {node_id}")

    def incoming_edge(node_id: str) -> str:
        for edge in net.getNode(str(node_id)).getIncoming():
            if _is_driveable(edge.getType()):
                return str(edge.getID())
        raise ValueError(f"No incoming edge found for node {node_id}")

    node_pairs = [(r.path[0], r.path[-1], r.num_people_on_route) for r in routes]
    edge_pairs = [
        (outgoing_edge(from_node), incoming_edge(to_node), k)
        for from_node, to_node, k in node_pairs
    ]

    valid_edge_pairs = [(out, inc, k) for out, inc, k in edge_pairs if out and inc]
    print(f"Routes with missing edges: {len(edge_pairs) - len(valid_edge_pairs)}")

    print("Running Polaris")
    result_paths = polaris_paths(valid_edge_pairs, graph, Weight.TRAVEL_TIME)

    print("Saving results")
    with open(f"{output_name}_polaris_paths.pkl", "wb") as f:
        pickle.dump(result_paths, f)

    stats = {
        "Amount of routes": _num_of_unique_paths(result_paths),
        "Amount of nodes with no route to safety": len(conf.origin_points) - len(paths),
    }

    return graph, result_paths, stats


EXCLUDED_HIGHWAY_TYPES = {
    "abandoned",
    "bridleway",
    "bus_guideway",
    "construction",
    "corridor",
    "cycleway",
    "elevator",
    "escalator",
    "footway",
    "no",
    "path",
    "pedestrian",
    "planned",
    "platform",
    "proposed",
    "raceway",
    "razed",
    "steps",
    "track",
}
EXCLUDED_SERVICE_TYPES = {"emergency_access", "parking", "parking_aisle", "private"}


def _is_driveable(edge_type: str) -> bool:
    """
    Check if the edge type is a public drivable road, as defined by OSMnx's `drive_service` filter.
    Reference: https://github.com/gboeing/osmnx/blob/d06a4404e9032652a95e9ff7151dc7f7cd485351/osmnx/_overpass.py#L85-L92
    :param edge_type: The type of the edge.
    :return: True if the edge is a public drivable road, False otherwise.
    """
    if edge_type.startswith("highway."):
        return edge_type.removeprefix("highway.") not in EXCLUDED_HIGHWAY_TYPES
    if edge_type.startswith("service."):
        return edge_type.removeprefix("service.") not in EXCLUDED_SERVICE_TYPES
    logging.warning(f"Edge type '{edge_type}' is not a valid road type.")
    return False


def _num_of_unique_paths(paths: list[list[dict[str, list[str] | list[int]]]]) -> int:
    """Count the number of unique paths in the given list of paths."""
    footprints: dict[str, int] = defaultdict(lambda: random.randint(0, 42_000_000))
    return len({sum(footprints[str(node)] for node in path[0]["ig"]) for path in paths})


if __name__ == "__main__":
    amager_input = set_amager_input_data()
    ravenna_input = set_ravenna_input_data()

    scenarios = [
        (FastestPath(), ravenna_input, "Ravenna - Polaris (3)", 3, "ravenna"),
        (FastestPath(), amager_input, "Amager - Polaris (1)", 1, "amager"),
        (FastestPath(), amager_input, "Amager - Polaris (3)", 3, "amager"),
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
            departure_times = _get_normal_dist_departure_time_list(
                len(paths), 0, conf.departure_end_time_sec
            )

            matsim_io.write_polaris_network(graph)
            matsim_io.write_polaris_plans(paths, departure_times)

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
            traceback.print_exc()
            logging.error(f"Error running algorithm {title}: {e}")

    create_comparison_dashboard(results)
