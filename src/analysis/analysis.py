import os
from pathlib import Path
from data_loader.population import get_total_population

from pyproj import Geod

from config import ProgramConfig


def write_analysis_data_simwrapper(
    program_conf: ProgramConfig, stats: dict[str, int], output_dir: Path
) -> None:
    """
    Write analysis data to the output directory.
    :param program_conf: ProgramConfig object containing simulation parameters
    :param stats: Dictionary containing statistics
    :param output_dir: Path to the output directory
    """
    _add_danger_zone_statistics(
        program_conf=program_conf,
        stats=stats,
        output_dir=output_dir,
    )
    _add_population_file_to_output(program_conf=program_conf, output_dir=output_dir)


def _add_danger_zone_statistics(
    program_conf: ProgramConfig, stats: dict[str, int], output_dir: Path
) -> None:
    geod = Geod(ellps="WGS84")

    # Compute area for each geometry in the GeoDataFrame and sum the results
    danger_zone_area_m2 = sum(
        geod.geometry_area_perimeter(geom)[0]
        for geom in program_conf.danger_zones.geometry
    )
    danger_zone_area_km2 = danger_zone_area_m2 / 1_000_000
    csv_file_path = os.path.join(output_dir, "danger_zone_data.csv")
    lengths = [
        data["length"] / 1000.0
        for _, _, _, data in program_conf.G.edges(keys=True, data=True)
        if "length" in data
    ]
    total_lane_km = sum(lengths)

    with open(csv_file_path, "w") as file:
        file.write("Info, Value\n")
        file.write(f"Danger Zone Area (km²),{round(danger_zone_area_km2, 2)}\n")
        file.write(
            f"Departure time window length [minutes], {program_conf.departure_end_time_sec / 60}\n"
        )
        file.write(f"Total lane km, {round(total_lane_km, 2)}\n")
        for key, value in stats.items():
            file.write(f"{key}, {value}\n")
        file.write(f"Total population, {get_total_population(program_conf.danger_zone_population_data, program_conf.cars_per_person)}\n")

def _add_population_file_to_output(
    program_conf: ProgramConfig, output_dir: Path
) -> None:
    pop_data = program_conf.danger_zone_population_data
    pop_data = pop_data.rename(columns={"id": "osm_id"})
    pop_data = pop_data.rename(columns={"pop": "population"})
    pop_data.to_file(
        os.path.join(output_dir, "population_data.geojson"), driver="GeoJSON"
    )
