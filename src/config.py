from dataclasses import dataclass, field
from pathlib import Path

import networkx as nx
from geopandas import GeoDataFrame

from data_loader import load_json_file_to_str
from input_data import InputData, PopulationType, SimulationType
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
RAVENNA_DANGER_ZONE = "ravenna.geojson"
RAVENNA_POPULATION_DATA = "ravennaPopulation.geojson"


TWO_MINUTES = 120
ONE_HOUR = 3600
ROUTE_ALGOS = [FastestPath(), ShortestPath()]

SIM_WRAPPER_CASE_STUDIES_LINK = (
    "https://docs.simwrapper.app/site/local/data/matsim/output/"
)


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
        populationType=PopulationType.GEO_JSON_FILE,
        simulationType=SimulationType.CASE_STUDIES,
        danger_zones_geopandas_json=load_json_file_to_str(CPH_AMAGER_DANGER_ZONE),
        pop_geo_json_filepath=CPH_POPULATION_DATA,
        cars_per_person=0.24,
    )


def set_amager_input_data() -> InputData:
    """
    Set the input data for development.
    """
    return InputData(
        populationType=PopulationType.GEO_JSON_FILE,
        simulationType=SimulationType.CASE_STUDIES,
        danger_zones_geopandas_json=load_json_file_to_str(CPH_AMAGER_DANGER_ZONE),
        pop_geo_json_filepath=CPH_POPULATION_DATA,
        cars_per_person=0.24,
    )


def set_ravenna_input_data() -> InputData:
    """
    Set the input data for development.
    """
    return InputData(
        populationType=PopulationType.GEO_JSON_FILE,
        simulationType=SimulationType.CASE_STUDIES,
        danger_zones_geopandas_json=load_json_file_to_str(RAVENNA_DANGER_ZONE),
        pop_geo_json_filepath=RAVENNA_POPULATION_DATA,
        cars_per_person=0.69,
    )


def set_small_data_input_data() -> InputData:
    """
    Set the input data for small data.
    """
    return InputData(
        populationType=PopulationType.NUMBER,
        simulationType=SimulationType.EXPLORE,
        population_number=1000,
        danger_zones_geopandas_json=load_json_file_to_str(CPH_SMALL_AMAGER_DANGER_ZONE),
        cars_per_person=0.24,
    )
