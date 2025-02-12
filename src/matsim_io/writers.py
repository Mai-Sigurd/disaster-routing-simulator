from typing import BinaryIO

from matsim.writers import XmlWriter

from matsim_io import kmh_to_ms

DANISH_SPEED_LIMIT = kmh_to_ms(130)


class NetworkWriter(XmlWriter):  # type: ignore[misc]
    FINISHED_SCOPE = 0
    NETWORK_SCOPE = 1
    NODES_SCOPE = 2
    LINKS_SCOPE = 3

    def __init__(self, writer: BinaryIO):
        XmlWriter.__init__(self, writer)

    def start_network(self, name: str | None = None) -> None:
        self._require_scope(self.NO_SCOPE)
        self._write_line('<?xml version="1.0" encoding="utf-8"?>')
        self._write_line(
            '<!DOCTYPE network SYSTEM "http://www.matsim.org/files/dtd/network_v2.dtd">'
        )
        self._write_line(f"<network{f' name="{name}"' if name else ''}>")
        self.indent += 1
        self.set_scope(self.NETWORK_SCOPE)

    def end_network(self) -> None:
        self._require_scope(self.NETWORK_SCOPE)
        self.indent -= 1
        self._write_line("</network>")
        self.set_scope(self.FINISHED_SCOPE)

    def start_nodes(self) -> None:
        self._require_scope(self.NETWORK_SCOPE)
        self._write_line("<nodes>")
        self.indent += 1
        self.set_scope(self.NODES_SCOPE)

    def end_nodes(self) -> None:
        self._require_scope(self.NODES_SCOPE)
        self.indent -= 1
        self._write_line("</nodes>")
        self.set_scope(self.NETWORK_SCOPE)

    def add_node(self, node_id: int, x: float, y: float) -> None:
        """
        Add a node to the network.
        :param node_id: Unique ID of the node.
        :param x: Latitude of the node.
        :param y: Longitude of the node.
        """
        assert 0 < node_id
        self._require_scope(self.NODES_SCOPE)
        self._write_line(f'<node id="{node_id}" x="{x}" y="{y}"/>')

    def start_links(self) -> None:
        self._require_scope(self.NETWORK_SCOPE)
        self._write_line("<links>")
        self.indent += 1
        self.set_scope(self.LINKS_SCOPE)

    def end_links(self) -> None:
        self._require_scope(self.LINKS_SCOPE)
        self.indent -= 1
        self._write_line("</links>")
        self.set_scope(self.NETWORK_SCOPE)

    def add_link(
        self,
        link_id: int,
        from_node: int,
        to_node: int,
        length: float,
        free_speed: float = DANISH_SPEED_LIMIT,
        perm_lanes: int | None = None,
    ) -> None:
        """
        Add a link to the network.
        :param link_id: Unique ID of the link.
        :param from_node: ID of the node where the link starts.
        :param to_node: ID of the node where the link ends.
        :param length: Length of the link in meters.
        :param free_speed: Maximum allowed speed of the link in meters per second.
        :param perm_lanes: Number of lanes on the link.
        """
        if perm_lanes is None:
            perm_lanes = 1
        assert 0 < link_id
        assert 0 < from_node
        assert 0 < to_node
        self._require_scope(self.LINKS_SCOPE)
        self._write_line(
            f'<link id="{link_id}"'
            f' from="{from_node}"'
            f' to="{to_node}"'
            f' length="{length}"'
            f' freespeed="{free_speed:.2f}"'
            f' permlanes="{perm_lanes}"/>'
        )
