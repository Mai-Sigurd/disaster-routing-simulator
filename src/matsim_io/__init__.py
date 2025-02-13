import matsim
import networkx as nx

from matsim_io.writers import NetworkWriter


def write_network(graph: nx.MultiDiGraph, name: str | None = None) -> None:
    def parse_min_int(value: str | list[str] | None) -> int | None:
        """
        Helper function to extract the minimum integer from a string or list of strings.
        In some cases, when a road has different speed limits, the max_speed of the simplified edge is a list.
        In those cases, we choose the minimum speed limit of the road.
        """
        if value is None:
            return None
        return min(map(int, value)) if isinstance(value, list) else int(value)

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
                speed_limit=parse_min_int(link_data.get("maxspeed")),
                perm_lanes=parse_min_int(link_data.get("lanes")),
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
