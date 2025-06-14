import logging
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

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
            "file": "analysis/analysis/trip_purposes_by_10_minutes.csv",
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
        return str(slugify(self.title))

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
    def trip_stats_csv_path(self) -> Path:
        """Path to the trip statistics analysis file."""
        return self.output_path / "analysis" / "analysis" / "trip_stats_disaster.csv"

    @property
    def danger_zone_data_csv_path(self) -> Path:
        """Path to the trip statistics analysis file."""
        return self.output_path / "analysis" / "danger_zone_data.csv"

    @property
    def trip_purposes_by_10_minutes_csv_path(self) -> str:
        """Path to the "trip_purposes_by_10_minutes" analysis file."""
        return f"{self.output_dir}/analysis/analysis/trip_purposes_by_10_minutes.csv"

    @property
    def traffic_stats_csv_path(self) -> str:
        """Path to the traffic statistics analysis file."""
        return f"{self.output_dir}/analysis/analysis/traffic_stats_by_road_type_and_hour.csv"

    @property
    def mode_share_csv_path(self) -> str:
        """Path to the "mode_share" analysis file."""
        return f"{self.output_dir}/analysis/population/mode_share.csv"


def create_comparison_dashboard(results: list[SimulationResult]) -> None:
    dashboard = {
        "header": {
            "title": "Comparison of different algorithms",
        },
        "layout": {
            "table_statistics": _create_statistics_tables(results),
            "people_in_safety": _add_people_in_safety_graph(results),
            "congestion_index_by_hour": _create_congestion_index_comparison(results),
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


def _add_people_in_safety_graph(
    results: list[SimulationResult],
) -> list[dict[str, Any]]:
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
            "colorRamp": "Viridis",
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


def _create_statistics_tables(results: list[SimulationResult]) -> list[dict[str, Any]]:
    return [
        _create_simulation_statistics_table(results),
        _create_evacuation_statistics_table(results),
    ]


def _create_simulation_statistics_table(
    results: list[SimulationResult],
) -> dict[str, Any]:
    """
    Create a table that combines simulation statistics from multiple simulations.
    Creates one column called "Value" since all the values are identical.
    Also performs a sanity check to verify that contents of different DFs are indeed identical.

    :param results: List of SimulationResult objects containing the paths to the simulation outputs.
    :return: A dashboard widget configuration.
    """
    dfs = [
        pd.read_csv(result.danger_zone_data_csv_path).rename(
            columns={" Value": "Value"}
        )
        for result in results
    ]

    output_file = "analysis/simulation_stats.csv"
    # Use the first result's data since they should all be identical
    _save_dataframe(dfs[0], MATSIM_DATA_DIR / output_file)

    return {
        "type": "csv",
        "title": "Simulation Statistics",
        "dataset": output_file,
        "showAllRows": True,
    }


def _create_evacuation_statistics_table(
    results: list[SimulationResult],
) -> dict[str, Any]:
    """
    Create a table that combines trip statistics from multiple simulations, showing one column per simulation.
    Each simulation's statistics will be in a column labeled with the algorithm's title.

    :param results: List of SimulationResult objects containing the paths to the simulation outputs.
    :return: A list of dashboard widget configurations.
    """
    dfs = [
        pd.read_csv(result.trip_stats_csv_path).rename(columns={"Value": result.title})
        for result in results
    ]

    merged_df = dfs[0]
    for df in dfs[1:]:
        merged_df = pd.merge(merged_df, df, on="Info", how="outer")

    required_metrics = [
        "Number of cars",
        "Total time traveled [h]",
        "Total distance traveled [km]",
        "Avg. speed [km/h]",
        "Avg. distance per trip [km]",
        "Avg. traveltime per trip [minutes]",
    ]

    filtered_df = merged_df[merged_df["Info"].isin(required_metrics)].copy()
    filtered_df["sort_key"] = filtered_df["Info"].apply(
        lambda x: required_metrics.index(x)
        if x in required_metrics
        else len(required_metrics)
    )
    filtered_df = filtered_df.sort_values("sort_key").drop("sort_key", axis=1)

    output_file = "analysis/combined_trip_stats_disaster.csv"
    _save_dataframe(filtered_df, MATSIM_DATA_DIR / output_file)

    return {
        "type": "csv",
        "title": "Evacuation Statistics",
        "dataset": output_file,
        "showAllRows": True,
    }


def create_bar_graph_mode_share(
    results: list[SimulationResult],
    y: str,
    x: str,
    title: str,
    description: str = "by 10-minute intervals",
    yaxis_title: str = "Number of people",
    xaxis_title: str = "Time from start of simulation (minutes)",
) -> list[dict[str, Any]]:
    return _create_bar_graph(
        results=results,
        y=y,
        title=title,
        x=x,
        description=description,
        yaxis_title=yaxis_title,
        xaxis_title=xaxis_title,
        datasets={
            r.label: {
                "file": r.mode_share_csv_path,
                "aggregate": {
                    "func": "SUM",
                    "groupBy": ["dist_group"],
                    "target": "share",
                },
            }
            for r in results
        },
    )


def create_bar_graph_trip_purpose(
    results: list[SimulationResult],
    y: str,
    x: str,
    title: str,
    description: str = "by 10-minute intervals",
    yaxis_title: str = "Number of people",
    xaxis_title: str = "Time from start of simulation (minutes)",
) -> list[dict[str, Any]]:
    return _create_bar_graph(
        results=results,
        y=y,
        title=title,
        x=x,
        description=description,
        yaxis_title=yaxis_title,
        xaxis_title=xaxis_title,
        datasets={r.label: r.trip_purposes_by_10_minutes_csv_path for r in results},
    )


def _create_bar_graph(
    results: list[SimulationResult],
    y: str,
    title: str,
    x: str,
    description: str,
    yaxis_title: str,
    xaxis_title: str,
    datasets: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
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
            "colorRamp": "Viridis",
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


def _create_congestion_index_comparison(
    results: list[SimulationResult],
) -> dict[str, Any]:
    """Create a comparison of the congestion index by hour for different simulation results."""
    return {
        "type": "plotly",
        "title": "Network congestion index",
        "description": "by hour",
        "datasets": {r.label: r.traffic_stats_csv_path for r in results},
        "traces": [
            {
                "x": f"${r.label}.hour",
                "y": f"${r.label}.congestion_index",
                "type": "scatter",
                "name": r.title,
            }
            for r in results
        ],
        "colorRamp": "Viridis",
        "layout": {
            "xaxis": {
                "title": "Hours after start of simulation",
                "color": "#444",
                "type": "-",
            },
            "yaxis": {"title": "Congestion index", "color": "#444", "type": "-"},
        },
    }


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
    _save_dataframe(merged_df, MATSIM_DATA_DIR / output_file)
    return output_file


def remove_unclassified_from_trip_stats_by_road_type_and_hour_csv(
    output_dir: str,
) -> None:
    """
    Remove the 'Unclassified' road type from the trip stat by road and hour CSV file.
    :param output_dir: Name of the output directory in the MATSim data directory.
    """
    file_path = (
        MATSIM_DATA_DIR
        / output_dir
        / "analysis"
        / "analysis"
        / "traffic_stats_by_road_type_and_hour.csv"
    )
    df = pd.read_csv(file_path)
    df = df[df["road_type"] != "unclassified"]
    df.to_csv(file_path, index=False)


def _save_dataframe(df: pd.DataFrame, path: Path) -> None:
    """
    Save a DataFrame to a CSV file at the specified path, ensuring the parent directory exists.
    :param df: DataFrame to save.
    :param path: Path where the CSV file will be saved, including the filename.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
