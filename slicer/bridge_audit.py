"""Measure slicer-classified bridge spans in Bambu Studio G-code."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import json
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile


NUMBER = r"-?(?:\d+(?:\.\d*)?|\.\d+)"
VALUE = re.compile(rf"([XYZE])({NUMBER})")


def project_labels(path: Path | None) -> dict[str, str]:
    if path is None:
        return {}
    with ZipFile(path) as archive:
        root = ET.fromstring(
            archive.read("Metadata/model_settings.config")
        )
    names = {}
    for node in root.findall("object"):
        metadata = {
            item.attrib["key"]: item.attrib["value"]
            for item in node.findall("metadata")
            if "key" in item.attrib and "value" in item.attrib
        }
        names[node.attrib["id"]] = metadata.get("name", node.attrib["id"])
    labels = {}
    for plate in root.findall("plate"):
        for instance in plate.findall("model_instance"):
            metadata = {
                item.attrib["key"]: item.attrib["value"]
                for item in instance.findall("metadata")
            }
            labels[metadata["identify_id"]] = names[metadata["object_id"]]
    return labels


def audit_plate(path: Path, labels: dict[str, str]) -> dict:
    feature = ""
    object_name = "unknown"
    layer: int | None = None
    x: float | None = None
    y: float | None = None
    segments: list[dict] = []

    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith("; layer num/total_layer_count:"):
            layer = int(line.split(":", 1)[1].strip().split("/", 1)[0])
        elif line.startswith("; FEATURE:"):
            feature = line.split(":", 1)[1].strip()
            continue
        elif line.startswith("; printing object "):
            object_name = line.removeprefix("; printing object ").split(
                " id:",
                1,
            )[0]
            continue
        elif line.startswith("; start printing object, unique label id:"):
            label = line.rsplit(":", 1)[1].strip()
            object_name = labels.get(label, f"label-{label}")
            continue

        if not line.startswith(("G0 ", "G1 ")):
            continue

        values = {key: float(value) for key, value in VALUE.findall(line)}
        next_x = values.get("X", x)
        next_y = values.get("Y", y)
        if (
            feature == "Bridge"
            and x is not None
            and y is not None
            and next_x is not None
            and next_y is not None
            and values.get("E", 0) > 0
        ):
            segments.append(
                {
                    "layer": layer,
                    "object": object_name,
                    "length_mm": math.hypot(next_x - x, next_y - y),
                    "start_mm": [x, y],
                    "end_mm": [next_x, next_y],
                }
            )
        x, y = next_x, next_y

    longest = max(segments, key=lambda item: item["length_mm"], default=None)
    objects = {}
    for item in segments:
        current = objects.setdefault(
            item["object"],
            {
                "bridge_segments": 0,
                "bridge_path_mm": 0.0,
                "max_bridge_segment_mm": 0.0,
            },
        )
        current["bridge_segments"] += 1
        current["bridge_path_mm"] += item["length_mm"]
        current["max_bridge_segment_mm"] = max(
            current["max_bridge_segment_mm"],
            item["length_mm"],
        )
    for current in objects.values():
        current["bridge_path_mm"] = round(current["bridge_path_mm"], 2)
        current["max_bridge_segment_mm"] = round(
            current["max_bridge_segment_mm"],
            2,
        )
    return {
        "file": path.name,
        "bridge_segments": len(segments),
        "bridge_layers": len({item["layer"] for item in segments}),
        "bridge_path_mm": round(
            sum(item["length_mm"] for item in segments),
            2,
        ),
        "max_bridge_segment_mm": round(
            longest["length_mm"] if longest else 0,
            2,
        ),
        "longest_segment": longest,
        "objects": objects,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("gcode_dir", type=Path)
    parser.add_argument("--project", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--max-span", type=float, default=20.0)
    args = parser.parse_args()

    plates = [
        audit_plate(path, project_labels(args.project))
        for path in sorted(args.gcode_dir.glob("plate_*.gcode"))
    ]
    report = {
        "maximum_allowed_span_mm": args.max_span,
        "maximum_observed_span_mm": max(
            (plate["max_bridge_segment_mm"] for plate in plates),
            default=0,
        ),
        "plates": plates,
    }
    text = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")

    if report["maximum_observed_span_mm"] > args.max_span:
        print(
            "WARNING: one or more bridge segments exceed "
            f"{args.max_span:.2f} mm",
        )


if __name__ == "__main__":
    main()
