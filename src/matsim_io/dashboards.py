import logging
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import geopandas as gpd
import pandas as pd
import yaml
from slugify import slugify

from data_loader.population import POPULATION
from input_data import PopulationType
from matsim_io import MATSIM_DATA_DIR

# Dashboard 1 is reserved for the top-level comparison dashboard.
dashboard_count = 2


def copy_dashboard(output_dir: str, dashboard_title: Optional[str] = None) -> None:
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
    shutil.copy(dashboard_path, dest_path)
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
    output_dir: str,
    danger_zone_population: gpd.GeoDataFrame,
    population_type: PopulationType,
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
    if population_type == PopulationType.NUMBER:
        breakpoints = ""
        steps = 1
    else:
        steps = 5
        breakpoints = f"{int(max_population * 0.2)}, {int(max_population * 0.4)}, {int(max_population * 0.6)}, {int(max_population * 0.8)}"

    population_map["display"] = {
        "fill": {
            "dataset": "population_data.geojson",
            "columnName": "population",
            "join": "",
            "colorRamp": {
                "ramp": "Viridis",
                "steps": steps,
                "breakpoints": breakpoints,
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


def change_departure_arrivals_bar_graph(output_dir: str) -> None:
    """
    Change the departure and arrivals bar graph in the dashboard file.
    """
    file_path = MATSIM_DATA_DIR / output_dir / "dashboard-2.yaml"
    data = yaml.safe_load(file_path.read_text(encoding="utf-8"))
    bar_graph = data["layout"]["departure-arrival"][0]
    bar_graph["title"] = "Departures and Arrivals"
    bar_graph["description"] = "by 10-minute intervals"
    bar_graph["datasets"] = {
        "dataset": {
            "file": "/analysis/analysis/trip_purposes_by_10_minutes.csv",
        }
    }
    bar_graph["traces"] = [
        {
            "x": "$dataset.bin",
            "y": "$dataset.arrival",
            "orientation": "v",
            "type": "bar",
            "name": "Arrival",
            "original_name": "Arrival",
        },
        {
            "x": "$dataset.bin",
            "y": "$dataset.departure",
            "type": "bar",
            "orientation": "v",
            "name": "Departure",
            "original_name": "Departure",
        },
    ]
    bar_graph["colorRamp"] = "Viridis"
    bar_graph["layout"] = {
        "xaxis": {
            "title": "Time from start of simulation (minutes)",
            "color": "#444",
            "type": "-",
        },
        "yaxis": {
            "title": "Number of people",
            "color": "#444",
            "type": "-",
        },
    }
    file_path.write_text(yaml.dump(data, sort_keys=False), encoding="utf-8")


@dataclass
class SimulationResult:
    output_dir: str
    """Name of the output directory of the simulation in the MATSim data directory."""
    title: str
    """Title of the simulation, used for display purposes."""

    @property
    def label(self) -> str:
        """Slugified title for use in file names and URLs."""
        return slugify(self.title)

    @property
    def output_path(self) -> Path:
        """Path to the output directory."""
        result: Path = MATSIM_DATA_DIR / self.output_dir
        return result

    @property
    def people_in_safety_csv_path(self) -> Path:
        """Path to the "people_in_safety" analysis file."""
        return self.output_path / "analysis" / "analysis" / "people_in_safety.csv"

    @property
    def trip_purposes_by_10_minutes_csv_path(self) -> str:
        """Path to the "trip_purposes_by_10_minutes" analysis file."""
        return f"{self.output_dir}/analysis/analysis/trip_purposes_by_10_minutes.csv"

    @property
    def mode_share_csv_path(self) -> str:
        """Path to the "mode_share" analysis file."""
        return f"{self.output_dir}/analysis/population/mode_share.csv"


def create_comparison_dashboard(results: list[SimulationResult]) -> None:
    dashboard = {
        "header": {
            "title": "Comparison of different algorithms",
            "description": "Comparison of different algorithms for routing out of the danger zone.",
        },
        "layout": {
            "people_in_safety": _add_people_in_safety_graph(results),
            "Trip_distance_distribution": create_bar_graph_mode_share(
                results=results,
                y="share",
                x="dist_group",
                title="Trip Distance Distribution",
                description="",
                yaxis_title="Proportion",
                xaxis_title="Meters",
            ),
            "departures": create_bar_graph_trip_purpose(
                results=results,
                y="departure",
                x="bin",
                title="Departures",
                description="by 10-minute intervals",
                yaxis_title="Number of people",
                xaxis_title="Time from start of simulation (minutes)",
            ),
            "arrivals": create_bar_graph_trip_purpose(
                results=results,
                y="arrival",
                x="bin",
                title="Arrivals",
                description="by 10-minute intervals",
                yaxis_title="Number of people",
                xaxis_title="Time from start of simulation (minutes)",
            ),
            "travel_time": create_bar_graph_trip_purpose(
                results,
                y="traveltime",
                x="bin",
                title="Travel Time",
                description="by 10-minute intervals",
                yaxis_title="Trips",
                xaxis_title="Time from departure to arrival (minutes)",
            ),
        },
    }

    dashboard_path = MATSIM_DATA_DIR / "dashboard-1.yaml"
    dashboard_path.write_text(yaml.dump(dashboard, sort_keys=False), encoding="utf-8")


def _add_people_in_safety_graph(results: list[SimulationResult]) -> list:  # type: ignore[type-arg]
    people_in_safety_csv_file = combine_csv_datasets(results)
    people_in_safety = [
        {
            "type": "plotly",
            "title": "People in Safety",
            "description": "Fraction of people in safety over time.",
            "datasets": {
                "dataset": people_in_safety_csv_file,
            },
            "traces": [
                {
                    "type": "scatter",
                    "x": "$dataset.bin",
                    "y": f"$dataset.cumulative_traveltime_{result.label}",
                    "name": f"{result.title}",
                    "original_name": f"{result.title}",
                    "mode": "lines",
                    "line": {
                        "width": 2,
                        "smoothing": 1,
                        "shape": "spline",
                        "dash": "solid",
                        "simplify": True,
                        "context": {
                            "width": 2,
                            "smoothing": 1,
                            "shape": "spline",
                            "dash": "solid",
                            "simplify": True,
                        },
                    },
                }
                for result in results
            ],
            "layout": {
                "xaxis": {
                    "title": "Time from start of simulation (minutes)",
                    "color": "#444",
                    "type": "-",
                },
                "yaxis": {
                    "title": "Fraction of people in safety",
                    "color": "#444",
                    "type": "-",
                },
            },
        }
    ]
    return people_in_safety


def create_bar_graph_mode_share(
    results: list[SimulationResult],
    y: str,
    x: str,
    title: str,
    description: str = "by 10-minute intervals",
    yaxis_title: str = "Number of people",
    xaxis_title: str = "Time from start of simulation (minutes)",
) -> list:  # type: ignore[type-arg]
    datasets = {}
    for result in results:
        datasets[result.label] = {
            "file": result.mode_share_csv_path,
            "aggregate": {
                "func": "SUM",
                "groupBy": ["dist_group"],
                "target": "share",
            },
        }

    return _create_bar_graph(
        results=results,
        y=y,
        title=title,
        x=x,
        description=description,
        yaxis_title=yaxis_title,
        xaxis_title=xaxis_title,
        datasets=datasets,
    )


def create_bar_graph_trip_purpose(
    results: list[SimulationResult],
    y: str,
    x: str,
    title: str,
    description: str = "by 10-minute intervals",
    yaxis_title: str = "Number of people",
    xaxis_title: str = "Time from start of simulation (minutes)",
) -> list:  # type: ignore[type-arg]
    datasets = {}
    for result in results:
        datasets[result.label] = result.trip_purposes_by_10_minutes_csv_path
    return _create_bar_graph(
        results=results,
        y=y,
        title=title,
        x=x,
        description=description,
        yaxis_title=yaxis_title,
        xaxis_title=xaxis_title,
        datasets=datasets,
    )


def _create_bar_graph(
    results: list[SimulationResult],
    y: str,
    title: str,
    x: str,
    description: str,
    yaxis_title: str,
    xaxis_title: str,
    datasets: dict,  # type: ignore[type-arg]
) -> list:  # type: ignore[type-arg]
    bar_graph = [
        {
            "type": "plotly",
            "title": title,
            "description": description,
            "datasets": datasets,
            "traces": [
                {
                    "x": f"${result.label}.{x}",
                    "y": f"${result.label}.{y}",
                    "orientation": "v",
                    "type": "bar",
                    "name": result.title,
                    "original_name": result.title,
                }
                for result in results
            ],
            "colorRamp": "RdYlBu",
            "layout": {
                "xaxis": {
                    "title": xaxis_title,
                    "color": "#444",
                    "type": "-",
                },
                "yaxis": {
                    "title": f"{yaxis_title}",
                    "color": "#444",
                    "type": "-",
                },
            },
        }
    ]
    return bar_graph


def combine_csv_datasets(results: list[SimulationResult]) -> str:
    """
    Combine multiple CSV datasets into a single CSV file.
    :param results: List of SimulationResult objects containing the paths to the CSV files.
    :return: Path to the combined CSV file, relative to the MATSim data directory.
    """
    dfs = [
        pd.read_csv(result.people_in_safety_csv_path)[
            ["bin", "cumulative_traveltime"]
        ].rename(
            columns={"cumulative_traveltime": f"cumulative_traveltime_{result.label}"}
        )
        for result in results
    ]

    merged_df = dfs[0]
    for df in dfs[1:]:
        merged_df = pd.merge(merged_df, df, on="bin", how="outer")
    merged_df.sort_values("bin", inplace=True)

    output_file = "analysis/people_in_safety.csv"
    merged_df.to_csv(MATSIM_DATA_DIR / output_file, index=False)
    return output_file
