import logging
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import pickle
from typing import cast

SRC_DIR = Path(__file__).resolve().parent.parent
INPUTDATADIR = SRC_DIR / "input_data.pickle"


class CITY(Enum):
    NONE = 1
    CPH = 2


class PopulationType(Enum):
    TIFF_FILE = 1
    GEO_JSON_FILE = 2
    NUMBER = 3


@dataclass
class InputData:
    type: PopulationType
    interval: int
    chunks: int
    city: CITY
    population_number: int
    osm_geopandas_json_bbox: str
    danger_zones_geopandas_json: str
    worldpop_filepath: str


def save_to_pickle(self: InputData, file_path: str) -> None:
    with open(file_path, "wb") as file:
        pickle.dump(self, file)


def open_pickle_file(file_path: str) -> InputData:
    with open(file_path, "rb") as file:
        inputdata = cast(InputData, pickle.load(file))
    # delete input_data.pickle file
    os.remove(file_path)
    return inputdata


def pretty_log(input_data: InputData) -> None:
    s = f"Input TYPE: {input_data.type}\nosm_geopandas_json: {input_data.osm_geopandas_json_bbox}\ndanger_zones_geopandas_json: {input_data.danger_zones_geopandas_json}\ninterval: {input_data.interval}\nchunks: {input_data.chunks}\npopulation_number: {input_data.population_number}\nworldpop_filepath: {input_data.worldpop_filepath}"
    logging.info(s)


def verify_input(input_data: InputData) -> tuple[bool, str]:
    if input_data.city == CITY.NONE and not os.path.exists(
        input_data.danger_zones_geopandas_json
    ):
        return False, "Dangerzones file not found"
    if input_data.type == PopulationType.GEO_JSON_FILE:
        if not os.path.exists(input_data.osm_geopandas_json_bbox):
            return False, "Geo JSON FILE not found"
    elif input_data.type == PopulationType.TIFF_FILE:
        if not os.path.exists(input_data.worldpop_filepath):
            return False, "Worldpop tiff file not found"
    elif input_data.type == PopulationType.NUMBER:
        if input_data.population_number <= 0:
            return False, "Population number must be greater than 0"
    return True, ""
