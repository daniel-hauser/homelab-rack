"""Compare no-support and targeted-support slices for the Pi HAT replacement."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from zipfile import ZipFile

from support_ab_audit import VALUE, support_stats


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PROTECTED = {
    "PRINT_THESE/STLs/04_Dual_Pi_Chassis.stl":
        "08fd7ff3386ccae4b3b88ac4285c3a5e85b7c5302bdfd340b1199e40791f42a4",
    "PRINT_THESE/STLs/05_Pi_Drawer_1.stl":
        "55c49cce449b605d9d9ece7d591c2a909a5cee9a78bc5e9efa26bcb8c575efb3",
    "PRINT_THESE/STLs/06_Pi_Drawer_2.stl":
        "b92f3a2b13bf54b023862d908b86916557379a7aaa5e19d9025a77635f92192f",
    "PRINT_THESE/STLs/07_Vent_Insert.stl":
        "1cfdda15ff2c9e3d9edf421483dd113ba1d133392142386c6ad1babb63f13df6",
    "PRINT_THESE/homelab-rack-Bambu-Studio-5-plates-NO-TEST.3mf":
        "b331e5667f108402b362110064e8334d73ac37c19ff9711615402e0f3ae45952",
    "PRINT_THESE/homelab-rack-Bambu-Studio-5-plates-NO-TEST-NO-SUPPORT.3mf":
        "59feb5793422088235ab3468d249bf7b7320294cbca494943d49c77d45fe89d5",
    "PRINT_THESE/homelab-rack-Bambu-Studio-6-plates.3mf":
        "4d211d8d3cbb81b5daf098624447622bd220b51a854fc8587bfec761f054e737",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def overhang_walls(path: Path) -> dict:
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
            feature == "Overhang wall"
            and x is not None
            and y is not None
            and next_x is not None
            and next_y is not None
            and values.get("E", 0) > 0
        ):
            length = math.hypot(next_x - x, next_y - y)
            if length > 0.01:
                segments.append(
                    {
                        "layer": layer,
                        "length_mm": round(length, 3),
                        "start_mm": [x, y],
                        "end_mm": [next_x, next_y],
                    }
                )
        x, y = next_x, next_y
    longest = max(segments, key=lambda item: item["length_mm"], default=None)
    rail_segments = [
        item
        for item in segments
        if item["length_mm"] > 40
        and 51.0 <= min(item["start_mm"][1], item["end_mm"][1])
        and max(item["start_mm"][1], item["end_mm"][1]) <= 61.0
        and (
            (
                25.0 <= min(item["start_mm"][0], item["end_mm"][0])
                and max(item["start_mm"][0], item["end_mm"][0]) <= 95.0
            )
            or (
                160.0 <= min(item["start_mm"][0], item["end_mm"][0])
                and max(item["start_mm"][0], item["end_mm"][0]) <= 227.0
            )
        )
    ]
    return {
        "segments": len(segments),
        "maximum_segment_mm": (
            longest["length_mm"] if longest is not None else 0
        ),
        "longest_segment": longest,
        "segments_over_40_mm": sum(
            item["length_mm"] > 40 for item in segments
        ),
        "raised_front_rail_segments": {
            "count": len(rail_segments),
            "maximum_mm": max(
                (item["length_mm"] for item in rail_segments), default=0
            ),
            "layers": sorted(
                {item["layer"] for item in rail_segments}
            ),
        },
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
    support = support_stats(args.targeted_dir / "plate_1.gcode")
    package = args.output.parent
    stl = package / "04_Dual_Pi_Chassis_5mm_HAT_Clearance.stl"
    project = (
        package / "homelab-rack-Dual-Pi-Chassis-5mm-HAT-Clearance.3mf"
    )
    with ZipFile(project) as archive:
        embedded_gcode = archive.read("Metadata/plate_1.gcode")
        embedded_md5 = archive.read(
            "Metadata/plate_1.gcode.md5"
        ).decode("ascii").strip().lower()
        crc_valid = archive.testzip() is None
        gcode_md5_valid = (
            hashlib.md5(embedded_gcode, usedforsecurity=False).hexdigest()
            == embedded_md5
        )
    report = {
        "decision": (
            "Use two build-plate-only manual support strips beneath the raised "
            "outer-bay front rails. The no-support slice emits 61.6 mm "
            "Overhang wall paths there; the strips are open to the front and "
            "do not enter the drawers, detent pockets, guide lips, vent bay, "
            "rails, magnets, rack ears, or chassis interior."
        ),
        "opening_heights_mm": [35.0, 30.0, 35.0],
        "opening_bottom_z_mm": 6.0,
        "front_clearance_depth_mm": 34.0,
        "remaining_top_rail_mm": 2.7,
        "top_rail_analysis": (
            "Each raised opening leaves a 2.7 mm-high by 3.0 mm-deep front "
            "fascia rail. The no-support slice places eight 61.6 mm Overhang "
            "wall paths at its first layer, so localized support is retained. "
            "The primary load path remains the unchanged base, corner posts, "
            "rack-ear bridges, stack-feature webs, seam towers, and rear "
            "brace towers; no reinforcement or interface change is required."
        ),
        "interior_clearance": (
            "The added cut passes through the full 34.0 mm front clearance "
            "depth. Mesh probes behind it find no roof or rib above the base, "
            "so the coils enter directly into the existing open interior."
        ),
        "baseline": {
            "totals": baseline["totals"],
            "warning_message": baseline["plates"][0]["warning_message"],
            "classified_max_bridge_mm": baseline_bridge[
                "maximum_observed_span_mm"
            ],
            "overhang_walls": overhang_walls(
                args.baseline_dir / "plate_1.gcode"
            ),
        },
        "targeted": {
            "totals": targeted["totals"],
            "warning_message": targeted["plates"][0]["warning_message"],
            "classified_max_bridge_mm": targeted_bridge[
                "maximum_observed_span_mm"
            ],
            "support_toolpaths": support,
        },
        "delta": {
            "grams": round(
                targeted["totals"]["grams"] - baseline["totals"]["grams"], 2
            ),
            "seconds": (
                targeted["totals"]["serial_seconds"]
                - baseline["totals"]["serial_seconds"]
            ),
        },
        "artifact_hashes": {
            "replacement_stl_sha256": digest(stl),
            "replacement_project_sha256": digest(project),
            "protected": {
                relative: {
                    "sha256": digest(ROOT / relative),
                    "unchanged": digest(ROOT / relative) == expected,
                }
                for relative, expected in EXPECTED_PROTECTED.items()
            },
        },
        "project_integrity": {
            "zip_crc_valid": crc_valid,
            "embedded_gcode_md5_valid": gcode_md5_valid,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
