## This file is for fetching the population data from datapop and outputting af GeoPandas dataframe with population snapped to nodes.
import logging
from pathlib import Path

import geopandas as gpd
import numpy as np
import osmnx as ox
import rasterio.warp
from networkx.classes import MultiDiGraph
from shapely.geometry import Point
from tqdm import tqdm

from data_loader import DATA_DIR
from data_loader.osm import download_cph
from data_loader.population.population import GEOMETRY, NODE_ID, POPULATION


def read_world_pop_data(tif_filename_path: Path) -> gpd.GeoDataFrame:
    with rasterio.open(tif_filename_path) as dataset:
        val = dataset.read(1)  # band 5
        no_data = dataset.nodata
        geometry = [
            Point(dataset.xy(x, y)[0], dataset.xy(x, y)[1])
            for x, y in np.ndindex(val.shape)
            if val[x, y] != no_data
        ]
        v = [val[x, y] for x, y in np.ndindex(val.shape) if val[x, y] != no_data]
        df = gpd.GeoDataFrame({"geometry": geometry, "data": v})
        df.crs = dataset.crs
    return df


def filter_world_pop_to_cph(df: gpd.GeoDataFrame, G: MultiDiGraph) -> gpd.GeoDataFrame:
    nodes, edges = ox.graph_to_gdfs(G)
    x_min, y_min, x_max, y_max = nodes.total_bounds
    gdf_filtered = df[
        (df.geometry.x > x_min)
        & (df.geometry.x < x_max)
        & (df.geometry.y > y_min)
        & (df.geometry.y < y_max)
    ]
    return gdf_filtered


def snap_population_to_nodes(
    df: gpd.GeoDataFrame, G: MultiDiGraph, maximum_distance_to_node: int
) -> gpd.GeoDataFrame:
    nearest_nodes_to_pop = {}
    nodes, edges = ox.graph_to_gdfs(G)
    for i in tqdm(df.index):
        point = df.loc[i].geometry
        pop = df.loc[i].data
        (nearest_node, dist) = ox.distance.nearest_nodes(
            G, point.x, point.y, return_dist=True
        )
        if dist < maximum_distance_to_node:
            if nearest_node not in nearest_nodes_to_pop:
                nearest_nodes_to_pop[nearest_node] = pop
            else:
                nearest_nodes_to_pop[nearest_node] += pop
    result = gpd.GeoDataFrame(
        {
            NODE_ID: list(nearest_nodes_to_pop.keys()),
            POPULATION: list(nearest_nodes_to_pop.values()),
            GEOMETRY: [nodes.loc[k].geometry for k in nearest_nodes_to_pop.keys()],
        },
        geometry=GEOMETRY,
    )
    if nodes.crs:
        result.set_crs(
            nodes.crs, inplace=True
        )  # Set Coordinate Reference System from nodes
    else:
        raise ValueError("Nodes GeoDataFrame has no CRS defined!")
    return result


def save_CPH_population_to_geojson() -> None:
    logging.getLogger().setLevel(logging.INFO)

    POPULATION_DATA_DIR = DATA_DIR / "population"
    POPULATION_DATA_FILE = POPULATION_DATA_DIR / "dnk_ppp_2020_constrained.tif"
    G = download_cph()
    logging.info("Graph downloaded")
    maximum_distance_to_node = 100

    snap_population_to_nodes(
        filter_world_pop_to_cph(read_world_pop_data(POPULATION_DATA_FILE), G),
        G,
        maximum_distance_to_node,
    ).to_file(
        POPULATION_DATA_DIR / "CPHpop.geojson",
        driver="GeoJSON",
    )


if __name__ == "__main__":
    save_CPH_population_to_geojson()
