import logging
from pathlib import Path
from typing import Optional

import geopandas as gpd
import yaml

from data_loader.population import POPULATION
from matsim_io import MATSIM_DATA_DIR

dashboard_count = 1


def move_dashboard(output_dir: str, dashboard_title: Optional[str] = None) -> None:
    """
    Moves the dashboard-2.yaml file in the given MATSim subdirectory up to the MATSim data directory.
    :param output_dir: Name of the output directory in the MATSim data directory.
    :param dashboard_title: Title for the dashboard. If None, the title will not be updated.
    """
    global dashboard_count

    output_path = MATSIM_DATA_DIR / output_dir
    if not output_path.is_dir():
        logging.error(f"Directory {output_path} does not exist.")
        return

    dashboard_path = output_path / "dashboard-2.yaml"
    if not dashboard_path.is_file():
        logging.error(f"Dashboard {dashboard_path} does not exist.")
        return

    dest_path = MATSIM_DATA_DIR / f"dashboard-{dashboard_count}.yaml"
    dashboard_path.rename(dest_path)
    dashboard_count += 1

    _rewrite_dashboard_dataset_paths(dest_path, output_dir)
    if dashboard_title:
        _update_dashboard_title(dest_path, dashboard_title)


def _rewrite_dashboard_dataset_paths(dashboard: Path, output_dir: str) -> None:
    """
    Rewrite the dataset paths in the dashboard file to point to the original output directory.
    :param dashboard: Path to the dashboard file.
    :param output_dir: Name of the output directory in the MATSim data directory.
    """
    original = dashboard.read_text(encoding="utf‑8")
    rewritten = "".join(
        line.replace("analysis/", f"{output_dir}/analysis/", 1)
        for line in original.splitlines(keepends=True)
    )
    dashboard.write_text(rewritten, encoding="utf-8")


def _update_dashboard_title(dashboard: Path, title: str) -> None:
    """
    Update the title of the given dashboard file.
    :param dashboard: Path to the dashboard file.
    :param title: New title for the dashboard.
    """
    data = yaml.safe_load(dashboard.read_text(encoding="utf-8"))
    data["header"]["title"] = title
    dashboard.write_text(yaml.dump(data, sort_keys=False), encoding="utf-8")


def append_breakpoints_to_congestion_map(output_dir: str) -> None:
    """
    Append breakpoints to the congestion map.
    """
    file_path = MATSIM_DATA_DIR / output_dir / "dashboard-2.yaml"
    data = yaml.safe_load(file_path.read_text(encoding="utf-8"))
    xytime_plot = data["layout"]["congestion_map"][0]
    xytime_plot["breakpoints"] = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    file_path.write_text(yaml.dump(data, sort_keys=False), encoding="utf-8")


def change_population_visuals_map(
    output_dir: str, danger_zone_population: gpd.GeoDataFrame
) -> None:
    """
    Change the population visuals map in the dashboard file.
    """
    max_population = round(danger_zone_population[POPULATION].max())

    file_path = MATSIM_DATA_DIR / output_dir / "dashboard-2.yaml"
    data = yaml.safe_load(file_path.read_text(encoding="utf-8"))
    population_map = data["layout"]["population"][0]
    population_map["shapes"] = {
        "file": "/analysis/population_data.geojson",
        "join": "osm_id",
    }
    population_map["datasets"] = {}
    population_map["display"] = {
        "fill": {
            "dataset": "population_data.geojson",
            "columnName": "population",
            "join": "",
            "colorRamp": {
                "ramp": "Viridis",
                "steps": 5,
                "breakpoints": f"{int(max_population * 0.2)}, {int(max_population * 0.4)}, {int(max_population * 0.6)}, {int(max_population * 0.8)}",
            },
        },
        "radius": {
            "dataset": "population_data.geojson",
            "columnName": "population",
            "scaleFactor": 3,
            "join": "",
        },
    }
    population_map["backgroundLayers"] = {}
    file_path.write_text(yaml.dump(data, sort_keys=False), encoding="utf-8")
