import json
import os


class InputData:
    def __init__(self) -> None:
        self.CPH_IS_CHOSEN = True
        self.osm_geopandas_json = ""
        self.danger_zones_geopandas_json = ""
        self.interval = 0
        self.chunks = 0
        self.worldpop = False
        self.population_number = 0
        self.worldpop_filepath = ""


def save_input_data(
    self: InputData,
    osm_geopandas_json: str,
    danger_zones_geopandas_json: str,
    interval: int,
    chunks: int,
    worldpop: bool,
    population_number: int,
    worldpop_filepath: str,
) -> None:
    self.osm_geopandas_json = osm_geopandas_json
    self.danger_zones_geopandas_json = danger_zones_geopandas_json
    self.interval = interval
    self.chunks = chunks
    self.worldpop = worldpop
    self.population_number = population_number
    self.worldpop_filepath = worldpop_filepath


def save_to_json_file(self: InputData, file_path: str) -> None:
    with open(file_path, "w") as file:
        json.dump(self.__dict__, file, indent=4)


def open_json_file(self: InputData, file_path: str) -> None:
    with open(file_path, "r") as file:
        data = json.load(file)
        self.__dict__.update(data)
    # delete json file
    os.remove(file_path)


def pretty_print(input_data: InputData) -> None:
    s = f"CPH_IS_CHOSEN: {input_data.CPH_IS_CHOSEN}\nosm_geopandas_json: {input_data.osm_geopandas_json}\ndanger_zones_geopandas_json: {input_data.danger_zones_geopandas_json}\ninterval: {input_data.interval}\nchunks: {input_data.chunks}\nworldpop: {input_data.worldpop}\npopulation_number: {input_data.population_number}\nworldpop_filepath: {input_data.worldpop_filepath}"
    print(s)
