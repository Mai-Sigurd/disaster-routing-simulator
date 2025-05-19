import logging

import geopandas as gpd
import networkx as nx
from shapely.geometry import Point

from data_loader.population.population_utils import (
    GEOMETRY,
    NODE_ID,
    POPULATION,
    POPULATION_DIR,
    save_tiff_population_to_geojson,
)


def get_origin_points(
    population_df: gpd.GeoDataFrame, dangerzone: gpd.GeoDataFrame
) -> list[str]:
    """
    Returns the origin points for the shortest path algorithm.
    :param population_df: A GeoDataFrame containing the population data.
    :param dangerzone: A GeoDataFrame containing the danger zone polygon(s).
    :return: A list of origin points in the dangerzone
    """
    # Get the origin points from the population data
    origin_points = distribute_population(
        danger_zone=dangerzone, population=population_df
    )

    # Convert the origin points to a list of strings
    return list(origin_points["id"])


def population_data_from_geojson(file_name: str) -> gpd.GeoDataFrame:
    """
    Loads a GeoJSON file and returns a GeoDataFrame.
    :param file_name: The name of the population GeoJSON file.
    :return: A GeoDataFrame containing the data from the GeoJSON file.
    """
    try:
        population = gpd.read_file(POPULATION_DIR / file_name)
        return population

    except Exception as e:
        logging.error(f"Error loading GeoJSON file: {e}")
        raise SystemExit


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
    tiff_file_path: str, geo_file_name: str, G: nx.MultiDiGraph
) -> gpd.GeoDataFrame:
    """
    Loads a TIFF file and returns a GeoDataFrame.
    :param tiff_file_path: The full path to the tiff file.
    :param geo_file_name: The name of the GeoJSON file the tiff information should be saved to.
    :param G: OSM graph.
    :return: A geopandas dataframe with id corresponding to OSM IDS and population, within the dangerzone.
    """
    save_tiff_population_to_geojson(
        tiff_file_path=tiff_file_path,
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

    if population_number < num_nodes:
        population_per_node = 0.0
    else:
        population_per_node = round(population_number / num_nodes)

    missing = int(population_number - (population_per_node * num_nodes))

    result = gpd.GeoDataFrame(
        {
            NODE_ID: nodes,
            POPULATION: [population_per_node] * num_nodes,
            GEOMETRY: [Point(G.nodes[node]["x"], G.nodes[node]["y"]) for node in nodes],
        },
        geometry=GEOMETRY,
    )
    if missing > 0:
        for i in range(missing):
            result.at[i, POPULATION] += 1

    result = result[result[POPULATION] > 0].reset_index(drop=True)
    return result


def get_total_population(
    population_data: gpd.GeoDataFrame, cars_per_person: float, danger_zone: gpd.GeoDataFrame = None
) -> int:
    if danger_zone is not None:
        logging.info("Calculation people in specific danger zone")
        population_data = gpd.sjoin(population_data, danger_zone, how="inner", predicate="intersects")
    result = population_data[POPULATION].sum()
    try:
        if result == 0:
            raise ValueError("Population data is 0")
        return int(result * cars_per_person)
    except TypeError:
        logging.error("Population data is empty")
        raise ValueError("Population data is empty")
