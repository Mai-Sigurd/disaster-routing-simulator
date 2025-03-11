import logging

import geopandas as gpd
import networkx as nx

from data_loader.population.utils import (
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
    :return: A geopandas dataframe with id corresponding to OSM IDS and population.
    """
    # List to store nodes in the danger zone and their population
    return gpd.sjoin(population, danger_zone, how="inner", predicate="intersects")


def population_data_from_tiff(
    tiff_file_name: str, geo_file_name: str, G: nx.MultiDiGraph
) -> gpd.GeoDataFrame:
    """
    Loads a TIFF file and returns a GeoDataFrame.
    :param file_name: The name of the TIFF file.
    :return: A GeoDataFrame containing the data from the TIFF file.
    """
    save_tiff_population_to_geojson(
        tiff_file_name=tiff_file_name,
        geo_file_name=geo_file_name,
        G=G,
        maximum_distance_to_node=100,
    )
    return population_data_from_geojson(geo_file_name)


def population_data_from_number(
    danger_zone: gpd.GeoDataFrame, population_number: int
) -> gpd.GeoDataFrame:
    """
    Creates a dataframe from the dangerzone, where each node has a evenly distributed population.
    :param danger_zone: A GeoDataFrame containing the danger zone polygon(s).
    :param population_number: The population number.
    :return: A GeoDataFrame containing the population number.
    """
    population = population_number / len(danger_zone)
    return gpd.GeoDataFrame(
        {
            "id": list(danger_zone.index),
            "population": [population] * len(danger_zone),
            "geometry": list(danger_zone.geometry),
        }
    )
