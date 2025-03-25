from dataclasses import dataclass, field
from pathlib import Path

import networkx as nx
from geopandas import GeoDataFrame

from routes.fastestpath import FastestPath
from routes.route_algo import RouteAlgo
from routes.shortestpath import ShortestPath

SOURCE_DIR = Path(__file__).parent.parent

CPH_G_GRAPHML = "copenhagen.graphml"
CPH_SMALL_AMAGER_DANGER_ZONE = "mindre_del_af_amager.geojson"
CPH_AMAGER_DANGER_ZONE = "dangerzone_amager.geojson"
CPH_POPULATION_DATA = "CPHpop.geojson"

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
