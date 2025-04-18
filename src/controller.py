import logging
import shutil
import subprocess
from types import FrameType

from analysis.analysis import write_danger_zone_data_simwrapper_csv
from config import (
    ROUTE_ALGOS,
    SOURCE_DIR,
    ProgramConfig,
)
from data_loader.danger_zones import load_danger_zone_from_str
from data_loader.osm import (
    download_osm_graph_from_polygon,
)
from data_loader.population import (
    get_origin_points,
    population_data_from_geojson,
    population_data_from_number,
    population_data_from_tiff,
)
from gui import close_gui, open_gui
from input_data import (
    INPUTDATADIR,
    InputData,
    PopulationType,
    SimulationType,
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


def controller_input_data(input_data: InputData) -> ProgramConfig:
    conf = ProgramConfig()
    conf.route_algos = ROUTE_ALGOS
    match input_data.simulation_type:
        case SimulationType.CASE_STUDIES:
            if input_data.danger_zones_geopandas_json == "":
                logging.fatal("Danger zone geojson is empty")
                raise ValueError("Danger zone geojson is empty")
            conf.G = download_osm_graph_from_polygon(
                input_data.danger_zones_geopandas_json
            )
            conf.danger_zones = load_danger_zone_from_str(
                input_data.danger_zones_geopandas_json, "EPSG:4326"
            )
            conf.danger_zone_population_data = population_data_from_geojson(
                input_data.pop_geo_json_filepath
            )
            conf.cars_per_person = input_data.cars_per_person

        case SimulationType.EXPLORE:
            conf.danger_zones = load_danger_zone_from_str(
                input_data.danger_zones_geopandas_json, "EPSG:4326"
            )
            conf.G = download_osm_graph_from_polygon(
                input_data.danger_zones_geopandas_json
            )
            conf.danger_zones = load_danger_zone_from_str(
                input_data.danger_zones_geopandas_json, "EPSG:4326"
            )
            match input_data.population_type:
                case PopulationType.TIFF_FILE:
                    conf.danger_zone_population_data = population_data_from_tiff(
                        tiff_file_path=input_data.worldpop_filepath,
                        geo_file_name=input_data.worldpop_filepath + "to_json.json",
                        G=conf.G,
                    )
                case PopulationType.NUMBER:
                    conf.danger_zone_population_data = population_data_from_number(
                        danger_zone=conf.danger_zones,
                        population_number=input_data.population_number,
                        G=conf.G,
                    )
                case PopulationType.GEO_JSON_FILE:
                    raise ValueError("Geojson file cannot be given in explore case")
    conf.origin_points = get_origin_points(
        conf.danger_zone_population_data, dangerzone=conf.danger_zones
    )
    conf.departure_end_time_sec = input_data.departure_end_time_sec
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
        return gui_handler(new_error_message)

    logging.info(input_data.pretty_summary())
    return input_data


def write_danger_zone_data(
    program_conf: ProgramConfig, stats: dict[str, int], filepath: str
) -> None:
    """
    Writes the total area of the danger zone and the total area of the city graph to a CSV file.
    """
    write_danger_zone_data_simwrapper_csv(
        program_conf=program_conf, stats=stats, filepath=filepath
    )


def gui_close(_signal: int, _frame: FrameType | None) -> None:
    """
    Close the GUI.
    """
    logging.info("Closing GUI")
    close_gui()
