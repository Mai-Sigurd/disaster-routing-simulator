import logging
import shutil
import subprocess
from types import FrameType

from config import (
    CPH_G_GRAPHML,
    CPH_POPULATION_DATA,
    CPH_SMALL_AMAGER_DANGER_ZONE,
    ROUTE_ALGOS,
    SOURCE_DIR,
    ProgramConfig,
)
from data_loader import load_json_file_to_str
from data_loader.danger_zones import load_danger_zone_from_str
from data_loader.osm import download_osm_graph_with_bbox_string, load_osm
from data_loader.population import (
    danger_zone_population,
    get_origin_points,
)
from gui import close_gui, open_gui
from input_data import (
    CITY,
    INPUTDATADIR,
    InputData,
    PopulationType,
    open_pickle_file,
    verify_input,
)
from matsim_io import MATSIM_DATA_DIR


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
        city=CITY.CPH,
        population_number=0,
        osm_geopandas_json_bbox="",
        danger_zones_geopandas_json=load_json_file_to_str(CPH_SMALL_AMAGER_DANGER_ZONE),
        worldpop_filepath="",
    )


def controller_input_data(input_data: InputData) -> ProgramConfig:
    conf = ProgramConfig()
    conf.route_algos = ROUTE_ALGOS
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
        conf.cars_per_person = 0.24
    if input_data.city == CITY.NONE:
        conf.G = download_osm_graph_with_bbox_string(input_data.osm_geopandas_json_bbox)
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
    logging.info(input_data.pretty_summary())
    return input_data


def gui_close(_signal: int, _frame: FrameType | None) -> None:
    """
    Close the GUI.
    """
    logging.info("Closing GUI")
    close_gui()
