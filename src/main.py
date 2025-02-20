import logging

from geopandas import GeoDataFrame

from data_loader.danger_zones import load_danger_zone
from data_loader.osm import download_cph, load_osm
from data_loader.population.population import (
    distribute_population,
    get_origin_points,
    load_geojson,
)
from matsim_io import write_network, write_plans
from routes.fastestpath import fastest_path
from routes.route import Route, create_route_objects
from routes.shortestpath import path

logging.basicConfig(
    level=logging.INFO,
    format="{asctime} [{levelname}] {message}",
    style="{",
)

CPH_LOADED = True


if __name__ == "__main__":
    if not CPH_LOADED:
        download_cph()
    G = load_osm("copenhagen.graphml")

    population_data: GeoDataFrame = load_geojson("CPHpop.geojson")

    danger_zones: GeoDataFrame = load_danger_zone(
        "mindre_del_af_amager.geojson", population_data.crs
    )
    danger_zone_population: GeoDataFrame = distribute_population(
        danger_zones, population_data
    )

    origin_points: list[str] = get_origin_points(danger_zone_population)
    #
    paths: list[path] = fastest_path(origin_points, danger_zones, G)
    routes: list[Route] = create_route_objects(
        list_of_paths=paths, population_data=population_data, chunks=1, interval=0
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
