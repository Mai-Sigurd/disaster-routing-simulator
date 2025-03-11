from enum import Enum

import geopandas as gpd
import networkx as nx

from data_loader.population.population import (
    distribute_population,
    population_data_from_geojson,
    population_data_from_number,
    population_data_from_tiff,
)


class PopulationType(Enum):
    TIFF_FILE = 1
    GEO_JSON_FILE = 2
    NUMBER = 3


def danger_zone_population(population_type: PopulationType, tiff_file_name: str, geo_file_name: str, population_number: int, danger_zone: gpd.GeoDataFrame, G: nx.MultiGraph) -> gpd.GeoDataFrame:
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
        return population_data_from_number(danger_zone, population_number)
    else: 
        pop_geo = population_data_from_geojson(danger_zone)
        return distribute_population(danger_zone, pop_geo)
    



def get_origin_points(population: gpd.GeoDataFrame) -> list[str]:
    """
    Returns the origin points for the shortest path algorithm.
    :param population: A GeoDataFrame containing the population data.
    :return: A list of origin points.
    """
    return list(population["id"])
