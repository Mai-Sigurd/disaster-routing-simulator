import logging
import shutil
import subprocess
from pathlib import Path

from geopandas import GeoDataFrame

from data_loader.danger_zones import load_danger_zone
from data_loader.osm import download_cph, load_osm, save_osm
from data_loader.population import (
    PopulationType,
    danger_zone_population,
    get_origin_points,
)
from matsim_io import MATSIM_DATA_DIR, write_network, write_plans
from routes.fastestpath import fastest_path
from routes.route import Route, create_route_objects
from routes.shortestpath import path

logging.basicConfig(
    level=logging.INFO,
    format="{asctime} [{levelname}] {message}",
    style="{",
)

SOURCE_DIR = Path(__file__).parent.parent
CPH_LOADED = True


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


if __name__ == "__main__":
    open_gui()

    input_data: InputData = InputData()
    open_json_file(self=input_data, file_path=INPUTDATADIR)
    pretty_print(input_data)
    # if not CPH_LOADED:
    #     G = download_cph()
    #     save_osm(G, "copenhagen.graphml")
    # else:
    #     G = load_osm("copenhagen.graphml")

    danger_zones: GeoDataFrame = load_danger_zone(
        "mindre_del_af_amager.geojson", "EPSG:4326"
    )
    danger_zone_population_data = danger_zone_population(
        population_type=PopulationType.GEO_JSON_FILE,
        tiff_file_name="",
        geo_file_name="CPHpop.geojson",
        population_number=0,
        danger_zone=danger_zones,
        G=G,
    )

    origin_points: list[str] = get_origin_points(danger_zone_population_data)

    paths: list[path] = fastest_path(origin_points, danger_zones, G)
    routes: list[Route] = create_route_objects(
        list_of_paths=paths,
        population_data=danger_zone_population_data,
        chunks=1,
        interval=0,
    )
    logging.info("Routes done")
    logging.info("Stats ---------------------")
    logging.info("Amount of routes: %s", len(routes))
    logging.info("Amount of people: %s", sum([r.num_people_on_route for r in routes]))
    logging.info(
        "Amount of nodes that could not reach dangerzone: %s",
        len(origin_points) - len(routes),
    )

    write_network(G, network_name="Copenhagen")
    write_plans(routes)

    run_matsim()
