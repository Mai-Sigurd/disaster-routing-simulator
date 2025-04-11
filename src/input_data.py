import json
import logging
import os
import pickle
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from textwrap import dedent
from typing import cast

SRC_DIR = Path(__file__).resolve().parent.parent
INPUTDATADIR = SRC_DIR / "input_data.pickle"


class SimulationType(Enum):
    EXPLORE = 1
    CASE_STUDIES = 2


class PopulationType(Enum):
    TIFF_FILE = 1
    GEO_JSON_FILE = 2
    NUMBER = 3


@dataclass
class InputData:
    population_type: PopulationType
    simulation_type: SimulationType
    danger_zones_geopandas_json: str
    departure_end_time_minute: int
    population_number: int = 0
    worldpop_filepath: str = ""
    cars_per_person: float = 1.0
    pop_geo_json_filepath: str = ""

    def pretty_summary(self) -> str:
        return dedent(f"""
            Simulation input summary:
            - Scenario type: {self.population_type}
            - Danger zones GeoJSON: {self.danger_zones_geopandas_json}
            - Population size: {self.population_number}
            - WorldPop file: {self.worldpop_filepath}
        """).strip()


def save_to_pickle(self: InputData, file_path: str) -> None:
    logging.info(f"Saving input data to {file_path}")
    with open(file_path, "wb") as file:
        pickle.dump(self, file)


def open_pickle_file(file_path: str) -> InputData:
    logging.info(f"Opening input data from {file_path}")
    with open(file_path, "rb") as file:
        inputdata = cast(InputData, pickle.load(file))
    # delete input_data.pickle file
    os.remove(file_path)
    return inputdata


def verify_input(input_data: InputData) -> tuple[bool, str]:
    ## CITY
    if input_data.simulation_type == SimulationType.EXPLORE:
        if input_data.danger_zones_geopandas_json == "":
            return False, "OSM dangerzone, geojson empty"
        if not _is_valid_geojson(input_data.danger_zones_geopandas_json):
            return False, "OSM dangerzone, Invalid geojson"
    if input_data.simulation_type == SimulationType.CASE_STUDIES:
        if input_data.danger_zones_geopandas_json != "" and not _is_valid_geojson(
            input_data.danger_zones_geopandas_json
        ):
            return False, "CPH city, danger zone is invalid geojson"

    ## POPULATION TYPE
    if input_data.population_type == PopulationType.TIFF_FILE:
        if input_data.worldpop_filepath == "":
            return False, "Worldpop tiff file path is empty"
        if not os.path.exists(input_data.worldpop_filepath):
            return False, "Worldpop tiff file not found"
    elif input_data.population_type == PopulationType.GEO_JSON_FILE:
        return True, ""
    elif input_data.population_type == PopulationType.NUMBER:
        if input_data.population_number <= 0:
            return False, "Population number must be greater than 0"
    return True, ""


def _is_valid_geojson(geojson_str: str) -> bool:
    try:
        data = json.loads(geojson_str)
        if isinstance(data, dict) and "type" in data:
            valid_types = {
                "Feature",
                "FeatureCollection",
                "Point",
                "LineString",
                "Polygon",
                "MultiPoint",
                "MultiLineString",
                "MultiPolygon",
                "GeometryCollection",
            }
            return data["type"] in valid_types
    except (json.JSONDecodeError, KeyError, TypeError):
        return False
    return False
