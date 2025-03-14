import logging
import shutil
import subprocess
from argparse import Namespace
from pathlib import Path
import signal

from geopandas import GeoDataFrame
from data_loader import load_json_file_to_str
from data_loader.danger_zones import load_danger_zone_from_str
from data_loader.osm import load_osm, download_osm_graph_geo_string
from data_loader.population import (
    danger_zone_population,
    get_origin_points,
)
from gui import open_gui, close_gui
from input_data import (
    INPUTDATADIR,
    InputData,
    open_pickle_file,
    pretty_log,
    verify_input,
    CITY,
    PopulationType,
)
from matsim_io import MATSIM_DATA_DIR, write_network, write_plans
from routes.fastestpath import fastest_path
from routes.route import Route, create_route_objects
from dataclasses import dataclass, field
from routes.shortestpath import path
import networkx as nx
import argparse


logging.basicConfig(
    level=logging.INFO,
    format="{asctime} [{levelname}] {message}",
    style="{",
)

SOURCE_DIR = Path(__file__).parent.parent

CPH_G_GRAPHML = "copenhagen.graphml"
CPH_SMALL_AMAGER_DANGER_ZONE = "mindre_del_af_amager.geojson"
CPH_AMAGER_DANGER_ZONE = "dangerzone_amager.geojson"
CPH_POPULATION_DATA = "CPHpop.geojson"


@dataclass
class ProgramConfig:
    danger_zone_population_data: GeoDataFrame = None
    danger_zones: GeoDataFrame = None
    G: nx.MultiDiGraph = None
    origin_points: list[str] = field(default_factory=list)


def run_matsim() -> None:
    """
    Run the MATSim executable with the config.xml file in the MATSIM_DATA_DIR.
    """
    matsim_output_dir = MATSIM_DATA_DIR / "output"
    if matsim_output_dir.exists() and matsim_output_dir.is_dir():
        shutil.rmtree(matsim_output_dir)

    cmd = [
        "mvn",
        "exec:java",
        "-Dexec.mainClass=org.disaster.routing.Main",
        "-Dexec.args=-Xmx6G",
    ]
    subprocess.run(cmd, cwd=SOURCE_DIR / "simulator")


def set_dev_input_data() -> InputData:
    """
    Set the input data for development.
    """
    return InputData(
        type=PopulationType.GEO_JSON_FILE,
        interval=0,
        chunks=0,
        city=CITY.CPH,
        population_number=0,
        osm_geopandas_json_bbox="",
        danger_zones_geopandas_json=load_json_file_to_str(CPH_SMALL_AMAGER_DANGER_ZONE),
        worldpop_filepath="",
    )


def controller_input_data(input_data: InputData) -> ProgramConfig:
    conf = ProgramConfig()
    if input_data.city == CITY.CPH:
        if input_data.danger_zones_geopandas_json == "":
            input_data.danger_zones_geopandas_json = load_json_file_to_str(
                CPH_SMALL_AMAGER_DANGER_ZONE
            )
        conf.G = load_osm(CPH_G_GRAPHML)
        conf.danger_zones = load_danger_zone_from_str(
            input_data.danger_zones_geopandas_json, "EPSG:4326"
        )
        conf.danger_zone_population_data = danger_zone_population(
            population_type=input_data.type,
            tiff_file_name="",
            geo_file_name=CPH_POPULATION_DATA,
            population_number=input_data.population_number,
            danger_zone=conf.danger_zones,
            G=conf.G,
        )
        conf.origin_points = get_origin_points(conf.danger_zone_population_data)
    if input_data.city == CITY.NONE:
        conf.G = download_osm_graph_geo_string(input_data.osm_geopandas_json_bbox)
        conf.danger_zones = load_danger_zone_from_str(
            input_data.danger_zones_geopandas_json, "EPSG:4326"
        )
        if input_data.type == PopulationType.TIFF_FILE:
            conf.danger_zone_population_data = danger_zone_population(
                population_type=input_data.type,
                tiff_file_name=input_data.worldpop_filepath,
                geo_file_name=input_data.danger_zones_geopandas_json,
                population_number=0,
                danger_zone=conf.danger_zones,
                G=conf.G,
            )
        else:  # PopulationType.NUMBER
            conf.danger_zone_population_data = danger_zone_population(
                population_type=input_data.type,
                tiff_file_name="",
                geo_file_name=input_data.danger_zones_geopandas_json,
                population_number=input_data.population_number,
                danger_zone=conf.danger_zones,
                G=conf.G,
            )
    return conf


def gui_handler(gui_error_message: str = "") -> InputData:
    open_gui(gui_error_message)
    try:
        input_data = open_pickle_file(file_path=INPUTDATADIR)
    except FileNotFoundError:
        logging.error("No input data found")
        raise SystemExit
    input_is_okay, new_error_message = verify_input(input_data)
    if not input_is_okay:
        gui_handler(new_error_message)
    pretty_log(input_data)
    return input_data


def start_up(args: Namespace) -> ProgramConfig:
    if not args.dev:
        input_data = gui_handler()
    else:
        logging.info("Dev mode enabled")
        input_data = set_dev_input_data()
        pretty_log(input_data)
        input_is_okay, error_message = verify_input(input_data)
        if not input_is_okay:
            logging.info("Error message: %s", error_message)
    return controller_input_data(input_data)


def main(args: Namespace) -> None:
    # TODO [ERROR] Error loading GeoJSON file:
    program_config = start_up(args)
    paths: list[path] = fastest_path(
        program_config.origin_points, program_config.danger_zones, program_config.G
    )
    routes: list[Route] = create_route_objects(
        list_of_paths=paths,
        population_data=program_config.danger_zone_population_data,
        chunks=1,
        interval=0,
    )
    logging.info("Routes done")
    logging.info("Stats ---------------------")
    logging.info("Amount of routes: %s", len(routes))
    logging.info("Amount of people: %s", sum([r.num_people_on_route for r in routes]))
    logging.info(
        "Amount of nodes that could not reach dangerzone: %s",
        len(program_config.origin_points) - len(routes),
    )

    write_network(program_config.G, network_name="Copenhagen")
    write_plans(routes)

    run_matsim()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-dev", action="store_true", help="Enable dev mode")
    parser.add_argument("-gui-only", action="store_true", help="Run GUI only")
    args = parser.parse_args()
    signal.signal(signal.SIGTSTP, close_gui)
    if args.gui_only:
        start_up(args)
    else:
        main(args)
