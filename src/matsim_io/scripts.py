import logging
from pathlib import Path

import yaml

from matsim_io import MATSIM_DATA_DIR


def move_dashboards(output_dirs: list[tuple[str, str]]) -> None:
    """
    Move every dashboard-2.yaml file in the given directories up to the MATSim data directory.
    :param output_dirs: List of tuples of MATSim subdirectories and SimWrapper titles.
    """

    for i, (output_dir, title) in enumerate(output_dirs, start=1):
        output_path = MATSIM_DATA_DIR / output_dir
        if not output_path.is_dir():
            logging.error(f"Directory {output_path} does not exist.")
            continue

        dashboard_path = output_path / "dashboard-2.yaml"
        if not dashboard_path.is_file():
            logging.error(f"Dashboard {dashboard_path} does not exist.")
            continue

        dest_path = MATSIM_DATA_DIR / f"dashboard-{i}.yaml"
        dashboard_path.rename(dest_path)
        _rewrite_dashboard_dataset_paths(dest_path, output_dir)
        _update_dashboard_title(dest_path, title)


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
