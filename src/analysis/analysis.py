from pyproj import Geod

from config import ProgramConfig


def write_danger_zone_data_simwrapper_csv(
    program_conf: ProgramConfig, stats: dict[str, int], filepath: str
) -> None:
    """
    Writes the total area of the danger zone and the total area of the city graph to a CSV file.
    :param program_conf: ProgramConfig object containing simulation parameters
    :param filepath: Path to the CSV file
    """
    geod = Geod(ellps="WGS84")

    # Compute area for each geometry in the GeoDataFrame and sum the results
    danger_zone_area_m2 = sum(
        geod.geometry_area_perimeter(geom)[0]
        for geom in program_conf.danger_zones.geometry
    )
    danger_zone_area_km2 = danger_zone_area_m2 / 1_000_000

    with open(filepath, "w") as file:
        file.write("Info, Value\n")
        file.write(f"Danger Zone Area (km²),{danger_zone_area_km2}\n")
        file.write(
            f"Departure distribution length in minutes, {program_conf.departure_end_time_sec / 60}\n"
        )
        for key, value in stats.items():
            file.write(f"{key}, {value}\n")
