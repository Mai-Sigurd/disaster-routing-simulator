import gzip
import logging
import random

import matsim
import networkx as nx

from data_loader import DATA_DIR
from matsim_io.writers import NetworkWriter

MATSIM_DATA_DIR = DATA_DIR / "matsim"


def write_network(
    graph: nx.MultiDiGraph,
    network_name: str | None = None,
    network_file: str = "network.xml",
    gzip_compress: bool = True,
) -> None:
    """
    Write a network to a MATSim network file.
    :param graph: NetworkX graph representing the network.
    :param network_name: Name of the network.
    :param network_file: Name of the output file.
    :param gzip_compress: Whether to save the file as a .gz compressed file.
    """
    if not network_file.endswith(".xml") or network_file.endswith(".xml.gz"):
        raise ValueError(
            f"Invalid file name: {network_file}. Expected .xml or .xml.gz file."
        )
    if gzip_compress and not network_file.endswith(".gz"):
        network_file += ".gz"

    logging.info(f"Writing MATSim network to {network_file}")

    open_func = gzip.open if gzip_compress else open
    with open_func(MATSIM_DATA_DIR / network_file, "wb+") as f_write:
        writer = NetworkWriter(f_write)  # type: ignore[arg-type]
        writer.start_network(network_name)

        writer.start_nodes()
        for node_id, node_data in graph.nodes(data=True):
            writer.add_node(node_id, node_data["x"], node_data["y"])
        writer.end_nodes()

        writer.start_links()
        for link_id, (from_node, to_node, link_data) in enumerate(
            graph.edges(data=True), 1
        ):
            writer.add_link(
                link_id,
                from_node,
                to_node,
                length=link_data["length"],
                speed_limit=_try_parse_min_int(link_data, "maxspeed"),
                perm_lanes=_try_parse_min_int(link_data, "lanes"),
            )
        writer.end_links()

        writer.end_network()

    logging.info(f"Finished writing MATSim network to {network_file}")


def write_plan(
    graph: nx.MultiDiGraph,
    plan_file: str = "plan.xml",
    gzip_compress: bool = True,
) -> None:
    if not plan_file.endswith(".xml") or plan_file.endswith(".xml.gz"):
        raise ValueError(
            f"Invalid file name: {plan_file}. Expected .xml or .xml.gz file."
        )
    if gzip_compress and not plan_file.endswith(".gz"):
        plan_file += ".gz"

    nodes = list(graph.nodes)

    open_func = gzip.open if gzip_compress else open
    with open_func(MATSIM_DATA_DIR / plan_file, "wb+") as f_write:
        writer = matsim.writers.PopulationWriter(f_write)

        writer.start_population()
        count = 0

        while count < 2500:
            v, w = random.sample(nodes, 2)
            if not nx.has_path(graph, v, w):
                continue
            v, w = graph.nodes[v], graph.nodes[w]
            dep_time = 60 * count
            for _ in range(5):
                writer.start_person(count)
                writer.start_plan(selected=True)
                writer.add_activity("danger", x=v["x"], y=v["y"], end_time=dep_time)
                writer.add_leg(mode="car", departure_time=dep_time)
                writer.add_activity("safe", x=w["x"], y=w["y"])
                writer.end_plan()
                writer.end_person()
                count += 1

        writer.end_population()


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
        logging.error(f"Invalid {key} value: {value}")
        return None
