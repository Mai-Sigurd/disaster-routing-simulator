from dataclasses import dataclass, field
from pathlib import Path

import networkx as nx
from geopandas import GeoDataFrame
from shapely.geometry.polygon import Polygon

from data_loader import load_json_file_to_str
from input_data import CITY, InputData, PopulationType
from routes.fastestpath import FastestPath
from routes.route_algo import RouteAlgo
from routes.shortestpath import ShortestPath

SOURCE_DIR = Path(__file__).parent.parent


CPH_G_GRAPHML = "copenhagen.graphml"
CPH_XTRA_SMALL_AMAGER_DANGER_ZONE = "dangerzone_lillebitteamager.geojson"
CPH_SMALL_AMAGER_DANGER_ZONE = "mindre_del_af_amager.geojson"
CPH_AMAGER_DANGER_ZONE = "dangerzone_amager.geojson"
CPH_POPULATION_DATA = "CPHpop.geojson"
CPH_AMAGER_BBOX = "bbox_amager.geojson"


TWO_MINUTES = 120
ONE_HOUR = 3600
ROUTE_ALGOS = [FastestPath(), ShortestPath()]


@dataclass
class ProgramConfig:
    danger_zone_population_data: GeoDataFrame = None
    danger_zones: GeoDataFrame = None
    G: nx.MultiDiGraph = None
    origin_points: list[str] = field(default_factory=list)
    cars_per_person: float = 1
    route_algos: list[RouteAlgo] = field(default_factory=list)


def set_dev_input_data() -> InputData:
    """
    Set the input data for development.
    """
    return InputData(
        type=PopulationType.GEO_JSON_FILE,
        city=CITY.CPH,
        population_number=0,
        danger_zones_geopandas_json=load_json_file_to_str(CPH_AMAGER_DANGER_ZONE),
        worldpop_filepath="",
    )


def set_small_data_input_data() -> InputData:
    """
    Set the input data for small data.
    """
    return InputData(
        type=PopulationType.NUMBER,
        city=CITY.NONE,
        population_number=1000,
        danger_zones_geopandas_json=load_json_file_to_str(CPH_SMALL_AMAGER_DANGER_ZONE),
        worldpop_filepath="",
    )
