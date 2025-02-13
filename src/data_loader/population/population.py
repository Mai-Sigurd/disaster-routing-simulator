import logging

import geopandas as gpd


def load_geojson(file_path: str) -> gpd.GeoDataFrame:
    """
    Loads a GeoJSON file and returns a GeoDataFrame.
    :param file_path: The path to the GeoJSON file.
    :return: A GeoDataFrame containing the data from the GeoJSON file.
    """
    try:
        return gpd.read_file(file_path)
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
