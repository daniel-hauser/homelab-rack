"""Generate audit evidence for the consolidated Pi replacement plate."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_OBJECTS = [
    "04_Dual_Pi_Chassis_5mm_HAT_Clearance.stl",
    "05_Pi_Drawer_1_6mm_Magnet_Fit.stl",
    "06_Pi_Drawer_2_6mm_Magnet_Fit.stl",
]
PROTECTED = {
    "PRINT_THESE/homelab-rack-Bambu-Studio-5-plates-NO-TEST.3mf":
        "b331e5667f108402b362110064e8334d73ac37c19ff9711615402e0f3ae45952",
    "PRINT_THESE/homelab-rack-Bambu-Studio-5-plates-NO-TEST-NO-SUPPORT.3mf":
        "59feb5793422088235ab3468d249bf7b7320294cbca494943d49c77d45fe89d5",
    "PRINT_THESE/homelab-rack-Bambu-Studio-6-plates.3mf":
        "4d211d8d3cbb81b5daf098624447622bd220b51a854fc8587bfec761f054e737",
    "PRINT_THESE/REPLACEMENTS/PI-HAT-5MM-CLEARANCE/"
    "04_Dual_Pi_Chassis_5mm_HAT_Clearance.stl":
        "759b33d0a4f450a061f606d94691d4a6cd5945e11bc3c48d9b70e3dd12183cc7",
    "PRINT_THESE/REPLACEMENTS/PI-HAT-5MM-CLEARANCE/bridge-audit.json":
        "500c5e1f2c080e677d4d599cec1399b172563d5649641d7b370809bf8a5d7c3a",
    "PRINT_THESE/REPLACEMENTS/PI-HAT-5MM-CLEARANCE/"
    "homelab-rack-Dual-Pi-Chassis-5mm-HAT-Clearance.3mf":
        "9094bb29cc75627325d7d7c94f37b7365854a6249794b2e64642c52a20ce2bf4",
    "PRINT_THESE/REPLACEMENTS/PI-HAT-5MM-CLEARANCE/"
    "no-support-bridge-audit.json":
        "342d8811a8bb4e016226fcac473ced97461f182af43acbe7dfcf973ecd5343af",
    "PRINT_THESE/REPLACEMENTS/PI-HAT-5MM-CLEARANCE/"
    "no-support-estimate.json":
        "6e1b88f2dd4bbd7db24a5da623a24a183a31e5d54a56ce8262ba2f4b54cd6f6e",
    "PRINT_THESE/REPLACEMENTS/PI-HAT-5MM-CLEARANCE/"
    "PI_HAT_5MM_CLEARANCE_AUDIT.json":
        "be30df79bbc6f423a7de2071c758003b01afd00c94bb81191fd94e6eb9641322",
    "PRINT_THESE/REPLACEMENTS/PI-HAT-5MM-CLEARANCE/"
    "pi_hat_5mm_clearance_front_cutaway.png":
        "008d28d65e85a416b2c4758aa2f591862bff98e97f38071ebfbe503dd6d3d796",
    "PRINT_THESE/REPLACEMENTS/PI-HAT-5MM-CLEARANCE/README.txt":
        "c2fe28b06f954c6b7c2b5dcdc60a038df079fc50061ce77b26a9dcb05964ccc5",
    "PRINT_THESE/REPLACEMENTS/PI-HAT-5MM-CLEARANCE/slice-estimate.json":
        "e215970421014f03863db75fe2fdbb5a0bc5c5f4137929b1f24935210a0f3f38",
    "PRINT_THESE/REPLACEMENTS/PI-HAT-5MM-CLEARANCE/support_toolpaths.png":
        "d64c5ae66770ea6d023066d7b09b8cdbc7aaceabeece1c19e2f6d7f682e84164",
    "PRINT_THESE/REPLACEMENTS/PI-MAGNET-POCKET-6MM/"
    "05_Pi_Drawer_1_6mm_Magnet_Fit.stl":
        "f8d8620ae080e8abb6807afddb5fe610690248605e3302816e0d2e5ebdd796d9",
    "PRINT_THESE/REPLACEMENTS/PI-MAGNET-POCKET-6MM/"
    "06_Pi_Drawer_2_6mm_Magnet_Fit.stl":
        "4c3f8aaa02c8579f0125a5ace3f0a7f1b74bc0d56e13efa3916921ccb25fa2f6",
    "PRINT_THESE/REPLACEMENTS/PI-MAGNET-POCKET-6MM/bridge-audit.json":
        "a7a162efa09003a0b0c31490f28f041f55b0877cfa1ad7ec6f4d9f93dd92f5cb",
    "PRINT_THESE/REPLACEMENTS/PI-MAGNET-POCKET-6MM/"
    "drawer-1-bridge-audit.json":
        "340bb6b92b7d63408a91c46e9d8774349b8ecf35d43ed3ed778c42db5803489c",
    "PRINT_THESE/REPLACEMENTS/PI-MAGNET-POCKET-6MM/"
    "drawer-1-estimate.json":
        "a83329596f0f111c883ef6f3b735871bc654fc4807b4c88b7454ca00c2fbf7df",
    "PRINT_THESE/REPLACEMENTS/PI-MAGNET-POCKET-6MM/"
    "drawer-2-bridge-audit.json":
        "340bb6b92b7d63408a91c46e9d8774349b8ecf35d43ed3ed778c42db5803489c",
    "PRINT_THESE/REPLACEMENTS/PI-MAGNET-POCKET-6MM/"
    "drawer-2-estimate.json":
        "715e6e1fb859ff87fd8ea3601528b4894cf66ef408bc5b88a1d956c066e48122",
    "PRINT_THESE/REPLACEMENTS/PI-MAGNET-POCKET-6MM/"
    "homelab-rack-Pi-Drawers-6mm-Magnet-Fit.3mf":
        "32755f0483f6580b6f596ef3eb76470d784f6f0c1f939ec3416048f200804013",
    "PRINT_THESE/REPLACEMENTS/PI-MAGNET-POCKET-6MM/"
    "PI_MAGNET_POCKET_6MM_AUDIT.json":
        "1352172b4a6a729e2131649ef55640f1709f50ce1a61ee89cc33229572d1faaa",
    "PRINT_THESE/REPLACEMENTS/PI-MAGNET-POCKET-6MM/"
    "pi_magnet_pocket_6mm_section.png":
        "6e7559d0fc10e004d951c0d70168eb157477b2865a8a2d29a7c30f859f7d3c86",
    "PRINT_THESE/REPLACEMENTS/PI-MAGNET-POCKET-6MM/README.txt":
        "e368247b071d9e56ea136bd82c7facef6ee1682ab5ba1cdc668b8406bb0a82ad",
    "PRINT_THESE/REPLACEMENTS/PI-MAGNET-POCKET-6MM/slice-estimate.json":
        "4f73a44c6fa67f4edc9c8f5c9fc05d33abe5046d225dd9fc44cb8264c280a338",
}
NUMBER = r"-?(?:\d+(?:\.\d*)?|\.\d+)"
VALUE = re.compile(rf"([XYZE])({NUMBER})")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def support_toolpaths(path: Path) -> dict:
    feature = ""
    layer = None
    x = None
    y = None
    points = []
    layers = set()
    segments = 0
    path_mm = 0.0
    regions = {"left": 0, "center": 0, "right": 0}
    for line in path.read_text(
        encoding="utf-8", errors="ignore"
    ).splitlines():
        if line.startswith("; layer num/total_layer_count:"):
            layer = int(line.split(":", 1)[1].split("/", 1)[0])
        elif line.startswith("; FEATURE:"):
            feature = line.split(":", 1)[1].strip()
            continue
        if not line.startswith(("G0 ", "G1 ")):
            continue
        values = {
            key: float(value) for key, value in VALUE.findall(line)
        }
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
                midpoint = (x + next_x) / 2
                region = (
                    "left"
                    if midpoint < 95
                    else "right"
                    if midpoint > 160
                    else "center"
                )
                regions[region] += 1
                points.extend([(x, y), (next_x, next_y)])
                layers.add(layer)
                segments += 1
                path_mm += length
        x, y = next_x, next_y
    return {
        "segments": segments,
        "path_mm": round(path_mm, 2),
        "layers": [min(layers), max(layers)],
        "bbox_mm": [
            round(min(point[0] for point in points), 2),
            round(min(point[1] for point in points), 2),
            round(max(point[0] for point in points), 2),
            round(max(point[1] for point in points), 2),
        ],
        "regions": regions,
    }


def pairwise_clearances(items: list[dict]) -> list[dict]:
    results = []
    for index, first in enumerate(items):
        for second in items[index + 1:]:
            a = first["bbox"]
            b = second["bbox"]
            x_gap = max(b[0] - a[2], a[0] - b[2], 0)
            y_gap = max(b[1] - a[3], a[1] - b[3], 0)
            overlap = x_gap == 0 and y_gap == 0
            results.append(
                {
                    "objects": [first["name"], second["name"]],
                    "x_gap_mm": round(x_gap, 2),
                    "y_gap_mm": round(y_gap, 2),
                    "overlap": overlap,
                }
            )
    return results


def integrity(project: Path) -> dict:
    with ZipFile(project) as archive:
        crc_valid = archive.testzip() is None
        gcode = archive.read("Metadata/plate_1.gcode")
        expected_md5 = archive.read(
            "Metadata/plate_1.gcode.md5"
        ).decode("ascii").strip().lower()
    return {
        "zip_crc_valid": crc_valid,
        "embedded_gcode_md5_valid": (
            hashlib.md5(gcode, usedforsecurity=False).hexdigest()
            == expected_md5
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("production_dir", type=Path)
    parser.add_argument("reopen_dir", type=Path)
    parser.add_argument("package_dir", type=Path)
    args = parser.parse_args()
    project = (
        args.package_dir
        / "homelab-rack-Pi-Complete-Single-Plate-A1.3mf"
    )
    estimate = load(args.production_dir / "estimate.json")
    bridge = load(args.production_dir / "bridge-audit.json")
    reopen_estimate = load(args.reopen_dir / "estimate.json")
    reopen_bridge = load(args.reopen_dir / "bridge-audit.json")

    with ZipFile(project) as archive:
        settings = ET.fromstring(
            archive.read("Metadata/model_settings.config")
        )
        plate = json.loads(archive.read("Metadata/plate_1.json"))
        project_settings = json.loads(
            archive.read("Metadata/project_settings.config")
        )
        enforcers = {
            node.find("./metadata[@key='name']").attrib["value"]: [
                part.find("./metadata[@key='name']").attrib["value"]
                for part in node.findall("part")
                if part.attrib.get("subtype") == "support_enforcer"
            ]
            for node in settings.findall("object")
        }
    names = [item["name"] for item in plate["bbox_objects"]]

    inventory = {
        "objects": plate["bbox_objects"],
        "object_names": names,
        "pairwise_clearances": pairwise_clearances(
            plate["bbox_objects"]
        ),
        "bed_bbox_mm": plate["bbox_all"],
        "bed_margins_mm": {
            "left": round(plate["bbox_all"][0], 2),
            "bottom": round(plate["bbox_all"][1], 2),
            "right": round(256 - plate["bbox_all"][2], 2),
            "top": round(256 - plate["bbox_all"][3], 2),
        },
    }
    support = support_toolpaths(args.production_dir / "plate_1.gcode")
    reopen_support = support_toolpaths(
        args.reopen_dir / "plate_1.gcode"
    )
    support.update(
        {
            "settings": {
                key: project_settings.get(key)
                for key in [
                    "enable_support",
                    "support_type",
                    "support_on_build_plate_only",
                    "support_top_z_distance",
                    "support_interface_top_layers",
                ]
            },
            "enforcers_by_object": enforcers,
            "drawers_receive_support": support["bbox_mm"][3] >= 171.6,
            "removal_access": (
                "Both support strips remain open to the front edge beneath "
                "the raised outer Pi-bay fascia rails. They are reachable "
                "from outside the empty chassis before drawer installation."
            ),
        }
    )
    protected = {
        relative: {
            "expected_sha256": expected,
            "actual_sha256": digest(ROOT / relative),
            "unchanged": digest(ROOT / relative) == expected,
        }
        for relative, expected in PROTECTED.items()
    }

    (args.package_dir / "object-inventory.json").write_text(
        json.dumps(inventory, indent=2) + "\n",
        encoding="utf-8",
    )
    (args.package_dir / "support-audit.json").write_text(
        json.dumps(support, indent=2) + "\n",
        encoding="utf-8",
    )
    (args.package_dir / "protected-hashes.json").write_text(
        json.dumps(protected, indent=2) + "\n",
        encoding="utf-8",
    )

    report = {
        "project": project.name,
        "slicer": "Bambu Studio 02.08.02.61",
        "printer": "Bambu Lab A1 / 0.4 mm nozzle / 256 x 256 mm",
        "profile": estimate["profile"],
        "inventory": inventory,
        "support": support,
        "slice": {
            "totals": estimate["totals"],
            "warning_message": estimate["plates"][0][
                "warning_message"
            ],
            "maximum_bridge_mm": bridge[
                "maximum_observed_span_mm"
            ],
        },
        "native_reopen_reslice": {
            "totals": reopen_estimate["totals"],
            "warning_message": reopen_estimate["plates"][0][
                "warning_message"
            ],
            "maximum_bridge_mm": reopen_bridge[
                "maximum_observed_span_mm"
            ],
            "difference_from_release_slice": {
                "grams": round(
                    reopen_estimate["totals"]["grams"]
                    - estimate["totals"]["grams"],
                    2,
                ),
                "seconds": (
                    reopen_estimate["totals"]["serial_seconds"]
                    - estimate["totals"]["serial_seconds"]
                ),
                "maximum_bridge_mm": round(
                    reopen_bridge["maximum_observed_span_mm"]
                    - bridge["maximum_observed_span_mm"],
                    2,
                ),
            },
            "support_toolpaths": reopen_support,
            **integrity(args.reopen_dir / "reopened.3mf"),
        },
        "project_integrity": integrity(project),
        "artifact_hashes": {
            path.name: digest(path)
            for path in [
                project,
                args.package_dir / "pi_complete_single_plate_bed.png",
                args.package_dir
                / "pi_complete_support_toolpaths.png",
            ]
        },
        "protected_hashes": protected,
    }
    (args.package_dir / "PI_COMPLETE_SINGLE_PLATE_AUDIT.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
