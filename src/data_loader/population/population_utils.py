## This file is for fetching the population data from datapop and outputting af GeoPandas dataframe with population snapped to nodes.
import logging

import geopandas as gpd
import networkx as nx
import numpy as np
import osmnx as ox
import rasterio.warp
from networkx.classes import MultiDiGraph
from shapely.geometry import Point
from tqdm import tqdm

from data_loader import DATA_DIR

POPULATION = "pop"
NODE_ID = "id"
GEOMETRY = "geometry"

POPULATION_DIR = DATA_DIR / "population"


def read_world_pop_data(tif_filename_path: str) -> gpd.GeoDataFrame:
    logging.info("Reading world population data from %s", tif_filename_path)
    with rasterio.open(tif_filename_path) as dataset:
        val = dataset.read(1)
        no_data = dataset.nodata
        geometry = [
            Point(dataset.xy(x, y)[0], dataset.xy(x, y)[1])
            for x, y in np.ndindex(val.shape)
            if val[x, y] != no_data
        ]
        v = [val[x, y] for x, y in np.ndindex(val.shape) if val[x, y] != no_data]
        df = gpd.GeoDataFrame({"geometry": geometry, "data": v})
        df.crs = dataset.crs
    logging.info("World population data read successfully")
    return df


def filter_world_pop_to_graph_area(
    df: gpd.GeoDataFrame, G: MultiDiGraph
) -> gpd.GeoDataFrame:
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
    pop_geo_frame: gpd.GeoDataFrame, G: MultiDiGraph, maximum_distance_to_node: int
) -> gpd.GeoDataFrame:
    """
    Snap population data to the nearest node in the graph.
    :param pop_geo_frame: GeoDataFrame with population data.
    :param G: OSM graph.
    :param maximum_distance_to_node: Maximum distance to snap population to a node in meters.
    :return: GeoDataFrame with population data snapped to nodes."""
    nearest_nodes_to_pop = {}
    nodes, edges = ox.graph_to_gdfs(G)
    for i in tqdm(pop_geo_frame.index):
        point = pop_geo_frame.loc[i].geometry
        pop = pop_geo_frame.loc[i].data
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


def save_tiff_population_to_geojson(
    tiff_file_path: str,
    geo_file_name: str,
    G: nx.MultiDiGraph,
    maximum_distance_to_node: int,
) -> None:
    """
    Save a TIFF file with population data to a GeoJSON file with population data snapped to nodes.
    :param tiff_file_path: Full filepath to the tif file
    :param geo_file_name: Name of the GeoJSON file that the tiff data should be saved to.
    :param G: OSM graph.
    :param maximum_distance_to_node: Maximum distance to snap population to a node in meters.
    """
    logging.info("Population data file: %s", tiff_file_path)

    snap_population_to_nodes(
        filter_world_pop_to_graph_area(read_world_pop_data(tiff_file_path), G),
        G,
        maximum_distance_to_node,
    ).to_file(
        POPULATION_DIR / geo_file_name,
        driver="GeoJSON",
    )
