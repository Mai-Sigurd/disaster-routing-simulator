import gzip
import logging
import os

import igraph
import networkx as nx
from matsim.writers import Id

from data_loader import DATA_DIR
from matsim_io.writers import NetworkWriter, PlansWriter
from routes.route import Route
from utils import kmh_to_ms

MATSIM_DATA_DIR = DATA_DIR / "matsim"
"""Directory where MATSim network and plan files are saved."""
LINK_IDS: dict[str, int] = {}
"""Dictionary mapping OSM link IDs to MATSim link IDs."""
DEFAULT_SPEED_LIMIT_DENMARK = 50
"""Default speed limit in Denmark in km/h."""

VISITED_EDGES = set()


def mat_sim_files_exist(plans_file: str, networks_file: str) -> bool:
    return os.path.exists(MATSIM_DATA_DIR / plans_file) and os.path.exists(
        MATSIM_DATA_DIR / networks_file
    )


def write_network(
    graph: nx.MultiDiGraph,
    network_name: str | None = None,
    network_filename: str = "network.xml",
    gzip_compress: bool = True,
) -> None:
    """
    Write a network to a MATSim network file.
    :param graph: NetworkX graph representing the network.
    :param network_name: Name of the network.
    :param network_filename: Name of the output file.
    :param gzip_compress: Whether to save the file as a .gz compressed file.
    """
    network_filename = _validate_and_format_filename(network_filename, gzip_compress)
    logging.info(f"Writing MATSim network to {network_filename}")

    open_func = gzip.open if gzip_compress else open
    with open_func(MATSIM_DATA_DIR / network_filename, "wb+") as f_write:
        writer = NetworkWriter(f_write)
        writer.start_network(network_name)

        writer.start_nodes()
        for node_id, node_data in graph.nodes(data=True):
            writer.add_node(node_id, node_data["x"], node_data["y"])
        writer.end_nodes()

        def _add_link(v: Id, w: Id, link_id: int) -> None:
            _add_link_id(v, w, link_id)
            writer.add_link(
                link_id,
                from_node=v,
                to_node=w,
                length=link_data["length"],
                speed_limit=kmh_to_ms(
                    _try_parse_min_int(link_data, "maxspeed")
                    or DEFAULT_SPEED_LIMIT_DENMARK
                ),
                perm_lanes=_try_parse_min_int(link_data, "lanes"),
            )

        writer.start_links()
        for link_id, (from_node, to_node, link_data) in enumerate(
            graph.edges(data=True)
        ):
            _add_link(from_node, to_node, link_id * 2)
            if not link_data["oneway"]:
                _add_link(to_node, from_node, link_id * 2 + 1)
        writer.end_links()

        writer.end_network()

    logging.info(f"Finished writing MATSim network to {network_filename}")


def write_plans(
    routes: list[Route],
    plan_filename: str = "plans.xml",
    gzip_compress: bool = True,
    mat_sim_routing: bool = False,
) -> None:
    """
    Write a MATSim plan file based on a given network and routes.
    :param routes: List of routes to turn into MATSim plans.
    :param plan_filename: Name of the output file.
    :param gzip_compress: Whether to save the file as a .gz compressed file.
    :param mat_sim_routing: Whether to use MATSim routing or not.
    """
    if not LINK_IDS:
        raise ValueError("No link IDs found. Please write the network first.")
    if not routes:
        logging.warning("No routes given. Writing empty MATSim plan file.")

    plan_filename = _validate_and_format_filename(plan_filename, gzip_compress)
    logging.info(f"Writing MATSim plans to {plan_filename}")

    open_func = gzip.open if gzip_compress else open
    with open_func(MATSIM_DATA_DIR / plan_filename, "wb+") as f_write:
        writer = PlansWriter(f_write)
        writer.start_population()
        count = 1
        for route in routes:
            count = _write_plan(route, writer, count, mat_sim_routing)
        writer.end_population()

    logging.info(f"Finished writing MATSim plans to {plan_filename}")


def write_polaris_network(
    graph: igraph.Graph,
    network_name: str | None = None,
    network_filename: str = "network.xml",
    gzip_compress: bool = True,
) -> None:
    """
    Write a network to a MATSim network file.
    :param graph: Graph representing the network.
    :param network_name: Name of the network.
    :param network_filename: Name of the output file.
    :param gzip_compress: Whether to save the file as a .gz compressed file.
    """
    network_filename = _validate_and_format_filename(network_filename, gzip_compress)
    logging.info(f"Writing MATSim network to {network_filename}")

    open_func = gzip.open if gzip_compress else open
    with open_func(MATSIM_DATA_DIR / network_filename, "wb+") as f_write:
        writer = NetworkWriter(f_write)
        writer.start_network(network_name)

        visited_nodes = set()
        writer.start_nodes()
        for edge in graph.es:
            from_node, from_coords = edge.source, edge["coordinates"]["from"]
            if from_node not in visited_nodes:
                writer.add_node(from_node, from_coords[0], from_coords[1])
                visited_nodes.add(from_node)
            to_node, to_coords = edge.target, edge["coordinates"]["to"]
            if to_node not in visited_nodes:
                writer.add_node(to_node, to_coords[0], to_coords[1])
                visited_nodes.add(to_node)
        writer.end_nodes()

        def _add_link(v: Id, w: Id, link_id: str) -> None:
            # if edge["length"] <= 0 or edge["speed_limit"] <= 0:
            #     logging.warning(f"Invalid edge data: {edge}")
            #     return
            speed_limit = (
                edge["speed_limit"]
                if edge["speed_limit"] > 0
                else DEFAULT_SPEED_LIMIT_DENMARK
            )
            writer.add_link(
                link_id,
                from_node=v,
                to_node=w,
                length=edge["length"],
                speed_limit=speed_limit,
                perm_lanes=1,  # TODO: Add perm_lanes attribute to edges
            )
            VISITED_EDGES.add(link_id)

        writer.start_links()
        for edge in graph.es:
            _add_link(edge.source, edge.target, edge.index)
        writer.end_links()

        writer.end_network()

    logging.info(f"Finished writing MATSim network to {network_filename}")


def write_polaris_plans(
    routes: list[list[dict[str, list[str] | list[int]]]],
    plan_filename: str = "plans.xml",
    gzip_compress: bool = True,
) -> None:
    """
    Write a MATSim plan file based on a given network and routes.
    :param routes: List of routes to turn into MATSim plans.
    :param plan_filename: Name of the output file.
    :param gzip_compress: Whether to save the file as a .gz compressed file.
    """
    if not routes:
        logging.warning("No routes given. Writing empty MATSim plan file.")

    plan_filename = _validate_and_format_filename(plan_filename, gzip_compress)
    logging.info(f"Writing MATSim plans to {plan_filename}")

    open_func = gzip.open if gzip_compress else open
    with open_func(MATSIM_DATA_DIR / plan_filename, "wb+") as f_write:
        writer = PlansWriter(f_write)
        writer.start_population()
        for i, route_list in enumerate(routes):
            route = route_list[0]["ig"]
            writer.start_person(i)
            writer.start_plan(selected=True)
            writer.add_activity_with_link("escape", link=route[0], end_time=0)
            writer.add_leg(route, departure_time=0)
            writer.add_activity_with_link("escape", link=route[-1])
            writer.end_plan()
            writer.end_person()
        writer.end_population()

    logging.info(f"Finished writing MATSim plans to {plan_filename}")


def _write_plan(
    route: Route, writer: PlansWriter, count: int, mat_sim_routing: bool
) -> int:
    node_pairs = list(zip(route.path[:-1], route.path[1:]))
    link_ids = [_get_link_id(v, w) for v, w in node_pairs]
    num_people = route.num_people_on_route
    for i in range(num_people):
        writer.start_person(count)
        writer.start_plan(selected=True)
        writer.add_activity_with_link(
            "escape", link=link_ids[0], end_time=route.departure_times[i]
        )
        writer.add_leg(
            link_ids,
            departure_time=route.departure_times[i],
            mat_sim_routing=mat_sim_routing,
        )
        writer.add_activity_with_link("escape", link=link_ids[-1])
        writer.end_plan()
        writer.end_person()
        count += 1
    return count


def _validate_and_format_filename(network_filename: str, gzip_compress: bool) -> str:
    """
    Helper function to check if the network file name is valid and add the .gz extension if needed.
    :param gzip_compress: Whether to save the file as a .gz compressed file.
    :param network_filename: Name of the output file.
    :return: Valid network file name.
    """
    if not (network_filename.endswith(".xml") or network_filename.endswith(".xml.gz")):
        raise ValueError(
            f"Invalid file name: {network_filename}. Expected .xml or .xml.gz file."
        )
    if gzip_compress and not network_filename.endswith(".gz"):
        return f"{network_filename}.gz"
    return network_filename


def _add_link_id(v: Id, w: Id, link_id: int) -> None:
    """
    Helper function to add a link ID to the LINK_IDS dictionary.
    :param v: OSM node ID.
    :param w: OSM node ID.
    :param link_id: MATSim link ID.
    """
    LINK_IDS[_link_key(v, w)] = link_id


def _get_link_id(v: Id, w: Id) -> int:
    """
    Helper function to get the link ID from the LINK_IDS dictionary.
    :param v: OSM node ID.
    :param w: OSM node ID.
    :return: MATSim link ID.
    :raises KeyError: If the link ID does not exist.
    """
    return LINK_IDS[_link_key(v, w)]


def _link_key(v: Id, w: Id) -> str:
    """
    Helper function to create a unique key for the LINK_IDS dictionary.
    :param v: OSM node ID.
    :param w: OSM node ID.
    :return: Unique key for the LINK_IDS dictionary.
    """
    return f"{v}-{w}"


def _try_parse_min_int(link_data: dict[str, list[str] | str], key: str) -> int | None:
    """
    Helper function to extract the minimum integer from a string or list of strings.
    In some cases, when a road has different speed limits, the max_speed of the simplified edge is a list.
    In those cases, we choose the minimum speed limit of the road.
    """
    value = link_data.get(key)
    if value is None:
        return None
    try:
        return min(map(int, value)) if isinstance(value, list) else int(value)
    except ValueError:
        logging.warning(f"Invalid {key} value for link {link_data['osmid']}: {value}")
        return None
