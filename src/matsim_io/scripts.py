import logging
from pathlib import Path

import yaml

from matsim_io import MATSIM_DATA_DIR


def append_breakpoints_to_congestion_map() -> None:
    """
    Append breakpoints to the congestion map.
    """
    file_path = MATSIM_DATA_DIR / "output/dashboard-2.yaml"
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
