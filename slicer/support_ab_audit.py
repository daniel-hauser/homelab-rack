"""Compare native Bambu no-support and targeted-support slices."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path


NUMBER = r"-?(?:\d+(?:\.\d*)?|\.\d+)"
VALUE = re.compile(rf"([XYZE])({NUMBER})")


def support_stats(path: Path) -> dict:
    feature = ""
    layer: int | None = None
    x: float | None = None
    y: float | None = None
    segments = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith("; layer num/total_layer_count:"):
            layer = int(line.split(":", 1)[1].split("/", 1)[0])
        elif line.startswith("; FEATURE:"):
            feature = line.split(":", 1)[1].strip()
            continue
        if not line.startswith(("G0 ", "G1 ")):
            continue
        values = {key: float(value) for key, value in VALUE.findall(line)}
        next_x = values.get("X", x)
        next_y = values.get("Y", y)
        if (
            feature.startswith("Support")
            and x is not None
            and y is not None
            and next_x is not None
            and next_y is not None
            and values.get("E", 0) > 0
        ):
            length = math.hypot(next_x - x, next_y - y)
            if length > 0.01:
                segments.append((x, y, next_x, next_y, layer, feature, length))
        x, y = next_x, next_y
    if not segments:
        return {
            "segments": 0,
            "path_mm": 0,
            "layers": [],
            "bbox_mm": None,
        }
    return {
        "segments": len(segments),
        "path_mm": round(sum(item[6] for item in segments), 2),
        "layers": [min(item[4] for item in segments), max(item[4] for item in segments)],
        "bbox_mm": [
            round(min(min(item[0], item[2]) for item in segments), 2),
            round(min(min(item[1], item[3]) for item in segments), 2),
            round(max(max(item[0], item[2]) for item in segments), 2),
            round(max(max(item[1], item[3]) for item in segments), 2),
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline_dir", type=Path)
    parser.add_argument("targeted_dir", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    baseline = json.loads(
        (args.baseline_dir / "estimate.json").read_text(encoding="utf-8")
    )
    targeted = json.loads(
        (args.targeted_dir / "estimate.json").read_text(encoding="utf-8")
    )
    baseline_bridge = json.loads(
        (args.baseline_dir / "bridge-audit.json").read_text(encoding="utf-8")
    )
    targeted_bridge = json.loads(
        (args.targeted_dir / "bridge-audit.json").read_text(encoding="utf-8")
    )
    plates = []
    for index, (before, after) in enumerate(
        zip(baseline["plates"], targeted["plates"]), start=1
    ):
        plates.append(
            {
                "plate": index,
                "objects": after["objects"],
                "baseline": {
                    "grams": before["g"],
                    "seconds": before["seconds"],
                    "warning_message": before["warning_message"],
                    "maximum_bridge_mm": baseline_bridge["plates"][
                        index - 1
                    ]["max_bridge_segment_mm"],
                },
                "targeted": {
                    "grams": after["g"],
                    "seconds": after["seconds"],
                    "warning_message": after["warning_message"],
                    "maximum_bridge_mm": targeted_bridge["plates"][
                        index - 1
                    ]["max_bridge_segment_mm"],
                    "support_toolpaths": support_stats(
                        args.targeted_dir / f"plate_{index}.gcode"
                    ),
                },
                "delta": {
                    "grams": round(after["g"] - before["g"], 2),
                    "seconds": after["seconds"] - before["seconds"],
                },
            }
        )
    report = {
        "analysis": (
            "The long upper paths are 17.51-17.52 mm forward seam-side "
            "corner-cap bridges, not roofs over the UCG/USW device cavities. "
            "The actual seam towers are farther rearward and remain excluded."
        ),
        "supported_feature": (
            "One reachable 7 x 7 mm manual support column under the forward "
            "seam-side top cap of the UCG chassis. The support "
            "starts on the internal bottom cap because build-plate-only "
            "support cannot reach the enclosed corner-post cavity."
        ),
        "usw_decision": (
            "No support is generated on either USW. Their seam-side forward "
            "cap overlaps the 34 mm-deep keystone clearance, while the "
            "opposite cap is part of the rack-ear/slot region. Supporting "
            "either would violate protected functional geometry for a "
            "17.52 mm bridge that already passes the native bridge gate."
        ),
        "explicit_exclusions": [
            "stack magnet pockets",
            "peg/socket interfaces",
            "seam keys and seam towers",
            "rack-ear slots",
            "device rails",
            "keystone openings",
            "rear-spine interfaces",
            "inaccessible rear corner cavities",
        ],
        "totals": {
            "baseline_grams": baseline["totals"]["grams"],
            "targeted_grams": targeted["totals"]["grams"],
            "support_delta_grams": round(
                targeted["totals"]["grams"] - baseline["totals"]["grams"], 2
            ),
            "baseline_seconds": baseline["totals"]["serial_seconds"],
            "targeted_seconds": targeted["totals"]["serial_seconds"],
            "support_delta_seconds": (
                targeted["totals"]["serial_seconds"]
                - baseline["totals"]["serial_seconds"]
            ),
        },
        "plates": plates,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
