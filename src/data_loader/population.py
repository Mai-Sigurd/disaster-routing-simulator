import geopandas as gpd

from interface import vertex


def distribute_population(danger_zone: gpd.GeoDataFrame) -> list[tuple[vertex, int]]:
    """
    Distributes the population of a danger zone across the surrounding areas.
    :return: A list of tuples where each tuple contains a coordinate and the number of people at that coordinate.
    """
    raise NotImplementedError
