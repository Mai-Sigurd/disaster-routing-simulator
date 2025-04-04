import geopandas as gpd
from pyproj import Geod


def write_g_and_danger_zone_data_simwrapper_csv(
    danger_zone: gpd.GeoDataFrame, filepath: str
) -> None:
    """
    Writes the total area of the danger zone and the total area of the city graph to a CSV file.

    :param danger_zone: GeoDataFrame containing the danger zone polygon(s)
    :param city_bbox_polygon: Polygon representing the city bounding box
    :param filepath: Path to the CSV file
    """
    geod = Geod(ellps="WGS84")

    # Compute area for each geometry in the GeoDataFrame and sum the results
    danger_zone_area_m2 = sum(
        geod.geometry_area_perimeter(geom)[0] for geom in danger_zone.geometry
    )
    danger_zone_area_km2 = danger_zone_area_m2 / 1_000_000

    with open(filepath, "w") as file:
        file.write("Area type, Area km^2\n")
        file.write(f"Danger zone,{danger_zone_area_km2}\n")
