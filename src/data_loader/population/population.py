import logging

import geopandas as gpd
import shapely


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
) -> list[tuple[shapely.geometry.point, int]]:
    """
    Returns the nodes in the danger zone and the number of people at each node.
    :return: A list of tuples where each tuple contains a coordinate and the number of people at that coordinate.
    """
    # List to store nodes in the danger zone and their population
    result = []

    # Iterate over the population nodes
    for idx, node in population.iterrows():
        point = node["geometry"]

        # Check if the point (node) is within any of the danger zone polygons
        if danger_zone.geometry.unary_union.contains(point):
            # Get the population at this node (e.g., from 'pop' column)
            population_count = node["pop"]

            # Append the result as a tuple (point, population_count)
            result.append((point, population_count))

    return result
