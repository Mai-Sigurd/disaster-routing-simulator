## This file is for fetching the population data from datapop and outputting af GeoPandas dataframe with population snapped to nodes.
import logging

import geopandas as gpd
import networkx as nx
import numpy as np
import osmnx as ox
import rasterio.warp
from shapely.geometry import Point
from tqdm import tqdm

tif_path = "../../../data/population/"
tif_filename = "dnk_ppp_2020_constrained.tif"
tif_filenamePath = f"{tif_path}{tif_filename}"
logging.getLogger().setLevel(logging.INFO)


def download_osm_graph(queries: list[str]) -> nx.MultiDiGraph:
    def download_query(query: str) -> nx.MultiDiGraph:
        logging.info(f"Downloading graph for {query}")
        city_graph = ox.graph_from_place(
            query, network_type="drive_service", simplify=True
        )
        logging.info(f"Downloaded graph for {query}")
        return city_graph

    return nx.compose_all([download_query(city) for city in queries])


G = download_osm_graph(
    [
        "Copenhagen Municipality, Denmark",
        "Frederiksberg Municipality, Denmark",
        "Tårnby Municipality, Denmark",
        "Hvidovre Municipality, Denmark",
        "Rødovre Municipality, Denmark",
        "Gentofte Municipality, Denmark",
        "Gladsaxe Municipality, Denmark",
        "Herlev Municipality, Denmark",
    ]
)
logging.info("Graph downloaded")
maximum_distance_to_node = 100


def read_world_pop_data() -> gpd.GeoDataFrame:
    with rasterio.open(tif_filenamePath) as dataset:
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


def filter_world_pop_to_cph(df: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    nodes, edges = ox.graph_to_gdfs(G)
    x_min, y_min, x_max, y_max = nodes.total_bounds
    gdf_filtered = df[
        (df.geometry.x > x_min)
        & (df.geometry.x < x_max)
        & (df.geometry.y > y_min)
        & (df.geometry.y < y_max)
    ]
    return gdf_filtered


def snap_population_to_nodes(df: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
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
            "id": list(nearest_nodes_to_pop.keys()),
            "pop": list(nearest_nodes_to_pop.values()),
            "geometry": [nodes.loc[k].geometry for k in nearest_nodes_to_pop.keys()],
        },
        geometry="geometry",
    )
    if nodes.crs:
        result.set_crs(
            nodes.crs, inplace=True
        )  # Set Coordinate Reference System from nodes
    else:
        raise ValueError("Nodes GeoDataFrame has no CRS defined!")
    return result


snap_population_to_nodes(filter_world_pop_to_cph(read_world_pop_data())).to_file(
    "../../../data/population/PopulationGeoDataframe.geojson", driver="GeoJSON"
)
