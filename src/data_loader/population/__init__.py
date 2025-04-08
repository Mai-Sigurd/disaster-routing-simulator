import geopandas as gpd
import networkx as nx

from data_loader.population.population import (
    distribute_population,
    population_data_from_geojson,
    population_data_from_number,
    population_data_from_tiff,
)
from input_data import PopulationType


def danger_zone_population(
    population_type: PopulationType,
    tiff_file_name: str,
    geo_file_name: str,
    population_number: int,
    danger_zone: gpd.GeoDataFrame,
    G: nx.MultiDiGraph,
) -> gpd.GeoDataFrame:
    """
    Returns the population data for the danger zone.
    :param population_type: The type of population data.
    :param tiff_file_name: The name of the TIFF file.
    :param geo_file_name: The name of the GeoJSON file.
    :param population_number: The population number.
    :param danger_zone: A GeoDataFrame containing the danger zone polygon(s).
    :param G: OSM graph.
    :return: A GeoDataFrame containing the population data for the danger zone.
    """
    if population_type == PopulationType.TIFF_FILE:
        return population_data_from_tiff(tiff_file_name, geo_file_name, G)
    elif population_type == PopulationType.NUMBER:
        return population_data_from_number(danger_zone, population_number, G)
    else:
        pop_geo = population_data_from_geojson(geo_file_name)
        return distribute_population(danger_zone, pop_geo)


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
