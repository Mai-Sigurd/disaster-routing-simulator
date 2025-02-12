import matsim
import networkx as nx

from matsim_io.writers import NetworkWriter


def write_network(graph: nx.MultiDiGraph, name: str | None = None) -> None:
    with open("network.xml", "wb+") as f_write:
        writer = NetworkWriter(f_write)
        writer.start_network(name)

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
                free_speed=kmh_to_ms(int(link_data["maxspeed"]))
                if "maxspeed" in link_data
                else None,
                perm_lanes=link_data.get("lanes"),
            )
        writer.end_links()

        writer.end_network()


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


def kmh_to_ms(kmh: float) -> float:
    """Convert km/h to m/s."""
    return kmh * 1000 / 3600
