import gzip
import logging

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

    def parse_min_int(value: str | list[str] | None) -> int | None:
        """
        Helper function to extract the minimum integer from a string or list of strings.
        In some cases, when a road has different speed limits, the max_speed of the simplified edge is a list.
        In those cases, we choose the minimum speed limit of the road.
        """
        if value is None:
            return None
        return min(map(int, value)) if isinstance(value, list) else int(value)

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
                speed_limit=parse_min_int(link_data.get("maxspeed")),
                perm_lanes=parse_min_int(link_data.get("lanes")),
            )
        writer.end_links()

        writer.end_network()

    logging.info(f"Finished writing MATSim network to {network_file}")


def write_plan() -> None:
    with open("plans.xml", "wb+") as f_write:
        writer = matsim.writers.PopulationWriter(f_write)

        writer.start_population()
        writer.start_person("person_id_123")
        writer.start_plan(selected=True)

        writer.add_activity(type="home", x=0.0, y=0.0, end_time=8 * 3600)
        writer.add_leg(mode="walk")
        writer.add_activity(type="work", x=10.0, y=0.0, end_time=18 * 3600)
        writer.add_leg(mode="pt")
        writer.add_activity(type="home", x=0.0, y=0.0)

        writer.end_plan()
        writer.end_person()

        writer.end_population()
