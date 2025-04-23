import logging
from pathlib import Path
from typing import Optional

import yaml

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
    lines = file_path.read_text(encoding="utf-8").splitlines(keepends=True)
    updated_lines = []
    inside_congestion_block = False

    for line in lines:
        updated_lines.append(line)

        # Detect start of congestion_map entry
        if line.strip() == "- type: xytime":
            inside_congestion_block = True

        # Find the right place to insert: after the last key in the block
        elif inside_congestion_block and (
            line.startswith("  ") and not line.startswith("    ")
        ):
            # This line is not part of the current item anymore
            updated_lines.insert(
                -1, "    breakpoints: [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]\n"
            )
            inside_congestion_block = False

    # Edge case: if it's the last block and never exited
    if inside_congestion_block:
        updated_lines.append("    breakpoints: [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]\n")

    file_path.write_text("".join(updated_lines), encoding="utf-8")
