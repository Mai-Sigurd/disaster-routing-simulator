import os

import geopandas as gpd
import wget

from interface import vertex

FILE_DIR = "data/worldpop"
url2020 = "https://data.worldpop.org/GIS/Population/Global_2000_2020/2020/DNK/dnk_ppp_2020_UNadj.tif"
path = FILE_DIR + "/dnk_ppp_2020_UNadj.tif"

def download_Population_data() -> None:
    """
    Downloads the population data for Denmark in 2020.
    """
    # if file dir empty download file
    if not os.path.isfile(path):
        wget.download(url2020, FILE_DIR)

def distribute_population(danger_zone: gpd.GeoDataFrame) -> list[tuple[vertex, int]]:
    """
    Distributes the worldpop of a danger zone across the surrounding areas.
    :return: A list of tuples where each tuple contains a coordinate and the number of people at that coordinate.
    """
    raise NotImplementedError
