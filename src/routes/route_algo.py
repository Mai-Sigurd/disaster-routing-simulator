import geopandas as gpd
import networkx as nx
import zope.interface

from routes.route_utils import path, vertex


class RouteAlgo(zope.interface.Interface):  # type: ignore
    def route_to_safety(
        self,
        origin_points: list[vertex],
        danger_zone: gpd.GeoDataFrame,
        G: nx.MultiDiGraph,
    ) -> list[path]:
        return []
