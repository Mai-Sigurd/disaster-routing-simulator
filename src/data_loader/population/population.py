import logging

import geopandas as gpd
import networkx as nx
from shapely.geometry import Point

from data_loader.population.utils import (
    GEOMETRY,
    NODE_ID,
    POPULATION,
    POPULATION_DIR,
    save_tiff_population_to_geojson,
)


def population_data_from_geojson(file_name: str) -> gpd.GeoDataFrame:
    """
    Loads a GeoJSON file and returns a GeoDataFrame.
    :param file_name: The name of the GeoJSON file.
    :return: A GeoDataFrame containing the data from the GeoJSON file.
    """
    try:
        return gpd.read_file(POPULATION_DIR / file_name)
    except Exception as e:
        logging.error(f"Error loading GeoJSON file: {e}")
        exit(0)


def distribute_population(
    danger_zone: gpd.GeoDataFrame, population: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """
    Returns the nodes in the danger zone and the number of people at each node.
    :return: A geopandas dataframe with id corresponding to OSM IDS and population, within the dangerzone.
    """
    # List to store nodes in the danger zone and their population
    return gpd.sjoin(population, danger_zone, how="inner", predicate="intersects")


def population_data_from_tiff(
    tiff_file_name: str, geo_file_name: str, G: nx.MultiDiGraph
) -> gpd.GeoDataFrame:
    """
    Loads a TIFF file and returns a GeoDataFrame.
    :param file_name: The name of the TIFF file.
    :return: A geopandas dataframe with id corresponding to OSM IDS and population, within the dangerzone.
    """
    save_tiff_population_to_geojson(
        tiff_file_name=tiff_file_name,
        geo_file_name=geo_file_name,
        G=G,
        maximum_distance_to_node=100,
    )
    return population_data_from_geojson(geo_file_name)


def population_data_from_number(
    danger_zone: gpd.GeoDataFrame, population_number: int, G: nx.MultiDiGraph
) -> gpd.GeoDataFrame:
    """
    Creates a dataframe with the population number divided by the number of nodes, where each node has a evenly distributed population.
    :param danger_zone: A GeoDataFrame containing the danger zone polygon(s).
    :param population_number: The population number.
    :return: A geopandas dataframe with id corresponding to OSM IDS and population, within the dangerzone.
    """
    nodes = [
        node
        for node, data in G.nodes(data=True)
        if any(
            polygon.intersects(Point(data["x"], data["y"]))
            for polygon in danger_zone.geometry
        )
    ]
    num_nodes = len(nodes)
    if num_nodes == 0:
        raise ValueError("No nodes found within the danger zone.")

    population_per_node = population_number / num_nodes

    result = gpd.GeoDataFrame(
        {
            NODE_ID: nodes,
            POPULATION: [population_per_node] * num_nodes,
            GEOMETRY: [Point(G.nodes[node]["x"], G.nodes[node]["y"]) for node in nodes],
        },
        geometry=GEOMETRY,
    )

    return result
