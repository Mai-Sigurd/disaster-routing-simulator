import logging

from geopandas import GeoDataFrame

from data_loader.danger_zones import load_danger_zone
from data_loader.osm import load_osm
from data_loader.population.population import (
    distribute_population,
    get_origin_points,
    load_geojson,
)
from routes.route import Route, create_route_objects
from routes.shortestpath import path, route_to_safety

logging.basicConfig(
    level=logging.INFO,
    format="{asctime} [{levelname}] {message}",
    style="{",
)


if __name__ == "__main__":
    # G = download_osm_graph(["Capital Region of Denmark"])
    # save_to_geojson()
    # G = download_osm_graph(
    #     [
    #         "Copenhagen Municipality, Denmark",
    #         "Frederiksberg Municipality, Denmark",
    #         "Tårnby Municipality, Denmark",
    #         "Hvidovre Municipality, Denmark",
    #         "Rødovre Municipality, Denmark",
    #         "Gentofte Municipality, Denmark",
    #         "Gladsaxe Municipality, Denmark",
    #         "Herlev Municipality, Denmark",
    #     ]
    # )
    # save_osm(G, "copenhagen.graphml")
    G = load_osm("copenhagen.graphml")
    populationData: GeoDataFrame = load_geojson(
        "../data/population/PopulationGeoDataframe.geojson"
    )
    danger_zones: GeoDataFrame = load_danger_zone(
        "dangerzone_amager.geojson", populationData.crs
    )
    danger_zone_population: GeoDataFrame = distribute_population(
        danger_zones, populationData
    )

    origin_points: list[str] = get_origin_points(danger_zone_population)
    paths: list[path] = route_to_safety(origin_points, danger_zones, G)
    routes: list[Route] = create_route_objects(
        list_of_paths=paths, population_data=populationData, chunks=1, interval=0
    )
