import gzip
import xml.etree.ElementTree as ET
from io import BytesIO
from pathlib import Path

import networkx as nx
import pytest

from matsim_io import NetworkWriter, write_network, write_plans
from routes.route import Route


@pytest.mark.parametrize(
    "gzip_compress, input_filename, expected_filename",
    [
        (False, "test_network.xml", "test_network.xml"),
        (True, "test_network.xml.gz", "test_network.xml.gz"),
        # Should end in .xml.gz even if .xml was passed
        (True, "test_network.xml", "test_network.xml.gz"),
    ],
)
def test_write_network(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_osm_graph: nx.MultiDiGraph,
    gzip_compress: bool,
    input_filename: str,
    expected_filename: str,
) -> None:
    """Test writing a MATSim network file ensuring correct file name formatting and content."""
    output_path = tmp_path / "matsim"
    output_path.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("matsim_io.MATSIM_DATA_DIR", output_path)

    write_network(
        mock_osm_graph, network_filename=input_filename, gzip_compress=gzip_compress
    )

    network_file = output_path / expected_filename
    assert network_file.exists(), f"Expected file {network_file} to exist."

    open_func = gzip.open if gzip_compress else open
    with open_func(network_file, "rt", encoding="utf-8") as f:
        tree = ET.parse(f)
        root = tree.getroot()

    assert root.tag == "network"

    nodes_element = root.find("nodes")
    assert nodes_element is not None, "Expected <nodes> element in XML."
    assert len(nodes_element.findall("node")) == len(mock_osm_graph.nodes)

    links_element = root.find("links")
    num_links = sum(
        (1 if data["oneway"] else 2) for _, _, data in mock_osm_graph.edges(data=True)
    )
    assert links_element is not None, "Expected <links> element in XML."
    assert len(links_element.findall("link")) == num_links


@pytest.mark.parametrize(
    "gzip_compress, input_filename, expected_filename",
    [
        (False, "test_plans.xml", "test_plans.xml"),
        (True, "test_plans.xml.gz", "test_plans.xml.gz"),
        # Should end in .xml.gz even if .xml was passed
        (True, "test_plans.xml", "test_plans.xml.gz"),
    ],
)
def test_write_plans(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_osm_graph: nx.MultiDiGraph,
    mock_routes: list[Route],
    gzip_compress: bool,
    input_filename: str,
    expected_filename: str,
) -> None:
    """Test writing a MATSim plans file ensuring correct file name formatting and content."""
    output_path = tmp_path / "matsim"
    output_path.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("matsim_io.MATSIM_DATA_DIR", output_path)

    # write_network is called to populate link IDs for write_plans
    write_network(mock_osm_graph)
    write_plans(
        mock_routes,
        plan_filename=input_filename,
        gzip_compress=gzip_compress,
        mat_sim_routing=False,
    )

    plans_file = output_path / expected_filename
    assert plans_file.exists(), f"Expected file {plans_file} to exist."

    open_func = gzip.open if gzip_compress else open
    with open_func(plans_file, "rt", encoding="utf-8") as f:
        tree = ET.parse(f)
        root = tree.getroot()

    assert root.tag == "population"

    people = root.findall("person")
    assert len(people) == sum(route.num_people_on_route for route in mock_routes)

    for person in people:
        plan = person.find("plan")
        assert plan is not None, "Expected <plan> element in XML."
        assert len(plan) == 3

        activity_danger, leg, activity_safe = plan
        assert activity_danger.attrib["link"] is not None
        assert leg.tag == "leg"
        assert leg.find("route") is not None
        assert activity_safe.attrib["link"] is not None


@pytest.mark.parametrize(
    "gzip_compress, input_filename, expected_filename",
    [
        (False, "test_plans.xml", "test_plans.xml"),
        (True, "test_plans.xml.gz", "test_plans.xml.gz"),
        # Should end in .xml.gz even if .xml was passed
        (True, "test_plans.xml", "test_plans.xml.gz"),
    ],
)
def test_write_plans_with_matsim_routing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_osm_graph: nx.MultiDiGraph,
    mock_routes: list[Route],
    gzip_compress: bool,
    input_filename: str,
    expected_filename: str,
) -> None:
    """Test writing a MATSim plans file ensuring correct file name formatting and content."""
    output_path = tmp_path / "matsim"
    output_path.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("matsim_io.MATSIM_DATA_DIR", output_path)

    # write_network is called to populate link IDs for write_plans
    write_network(mock_osm_graph)
    write_plans(
        mock_routes,
        plan_filename=input_filename,
        gzip_compress=gzip_compress,
        mat_sim_routing=True,
    )

    plans_file = output_path / expected_filename
    assert plans_file.exists(), f"Expected file {plans_file} to exist."

    open_func = gzip.open if gzip_compress else open
    with open_func(plans_file, "rt", encoding="utf-8") as f:
        tree = ET.parse(f)
        root = tree.getroot()

    assert root.tag == "population"

    people = root.findall("person")
    assert len(people) == sum(route.num_people_on_route for route in mock_routes)

    for person in people:
        plan = person.find("plan")
        assert plan is not None, "Expected <plan> element in XML."
        assert len(plan) == 3

        activity_danger, leg, activity_safe = plan
        assert activity_danger.attrib["link"] is not None
        assert leg.tag == "leg"
        assert leg.find("route") is None
        assert activity_safe.attrib["link"] is not None


@pytest.mark.parametrize(
    "network_name",
    [
        "Copenhagen",
        "Gotham",
        None,
    ],
)
def test_network_name(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_osm_graph: nx.MultiDiGraph,
    network_name: str | None,
) -> None:
    """Test that the network name is correctly set in the XML output."""
    output_path = tmp_path / "matsim"
    output_path.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("matsim_io.MATSIM_DATA_DIR", output_path)

    write_network(
        mock_osm_graph,
        network_name=network_name,
    )

    network_file = output_path / "network.xml.gz"
    assert network_file.exists(), f"Expected file {network_file} to exist."

    with gzip.open(network_file, "rt", encoding="utf-8") as f:
        tree = ET.parse(f)
        root = tree.getroot()

    assert root.tag == "network"
    if network_name is None:
        assert "name" not in root.attrib
    else:
        assert root.attrib["name"] == network_name


def test_add_link_invalid_params() -> None:
    """Test that add_link raises an AssertionError for invalid parameters."""
    writer = NetworkWriter(BytesIO())

    with pytest.raises(AssertionError, match="length must be a positive number"):
        writer.add_link(1, 2, 3, length=-100, speed_limit=50)

    with pytest.raises(AssertionError, match="speed_limit must be a positive number"):
        writer.add_link(1, 2, 3, length=100, speed_limit=-50)

    with pytest.raises(AssertionError, match="perm_lanes must be a positive integer"):
        writer.add_link(1, 2, 3, length=100, speed_limit=50, perm_lanes=0)
