"""Generate the Pi drawer magnet-pocket replacement release audit."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
PROTECTED = {
    "PRINT_THESE/STLs/01_UCG_Ultra.stl":
        "285683acebcf1558ec7f9b099929a86e004c7bd8cb1da604708ba6a67f011c53",
    "PRINT_THESE/STLs/02_USW_Ultra_Left.stl":
        "d170ff259a666a326cfc8dd37e05b264912834ac23a488023032b5031e7e7c29",
    "PRINT_THESE/STLs/03_USW_Ultra_Right.stl":
        "a6d820ee7f390152fce467c214d1f5b25e861bb094ed32e06bbe30e26909ff85",
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
    "PRINT_THESE/REPLACEMENTS/PI-HAT-5MM-CLEARANCE/no-support-estimate.json":
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
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("drawer_1_dir", type=Path)
    parser.add_argument("drawer_2_dir", type=Path)
    parser.add_argument("combined_dir", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--reopen-dir", type=Path)
    args = parser.parse_args()
    package = args.output.parent
    project = package / "homelab-rack-Pi-Drawers-6mm-Magnet-Fit.3mf"

    estimates = {
        "drawer_1": load_json(args.drawer_1_dir / "estimate.json"),
        "drawer_2": load_json(args.drawer_2_dir / "estimate.json"),
        "combined": load_json(args.combined_dir / "estimate.json"),
    }
    bridges = {
        "drawer_1": load_json(args.drawer_1_dir / "bridge-audit.json"),
        "drawer_2": load_json(args.drawer_2_dir / "bridge-audit.json"),
        "combined": load_json(args.combined_dir / "bridge-audit.json"),
    }
    reopen = None
    if args.reopen_dir:
        reopen_estimate = load_json(args.reopen_dir / "estimate.json")
        reopen_bridge = load_json(args.reopen_dir / "bridge-audit.json")
        reopened_project = args.reopen_dir / "reopened.3mf"
        with ZipFile(reopened_project) as archive:
            reopened_crc_valid = archive.testzip() is None
            reopened_gcode = archive.read("Metadata/plate_1.gcode")
            reopened_md5 = archive.read(
                "Metadata/plate_1.gcode.md5"
            ).decode("ascii").strip().lower()
        reopen = {
            "reopened_project_crc_valid": reopened_crc_valid,
            "embedded_gcode_md5_valid": (
                hashlib.md5(
                    reopened_gcode, usedforsecurity=False
                ).hexdigest()
                == reopened_md5
            ),
            "totals": reopen_estimate["totals"],
            "warning_message": reopen_estimate["plates"][0][
                "warning_message"
            ],
            "maximum_bridge_mm": reopen_bridge[
                "maximum_observed_span_mm"
            ],
            "support_toolpaths": (
                "; FEATURE: Support" in reopened_gcode.decode(
                    "utf-8", errors="ignore"
                )
            ),
            "difference_from_release_slice": {
                "grams": round(
                    reopen_estimate["totals"]["grams"]
                    - estimates["combined"]["totals"]["grams"],
                    2,
                ),
                "seconds": (
                    reopen_estimate["totals"]["serial_seconds"]
                    - estimates["combined"]["totals"]["serial_seconds"]
                ),
                "maximum_bridge_mm": round(
                    reopen_bridge["maximum_observed_span_mm"]
                    - bridges["combined"]["maximum_observed_span_mm"],
                    2,
                ),
            },
        }
    with ZipFile(project) as archive:
        crc_valid = archive.testzip() is None
        gcode = archive.read("Metadata/plate_1.gcode")
        expected_md5 = archive.read(
            "Metadata/plate_1.gcode.md5"
        ).decode("ascii").strip().lower()
        settings = ET.fromstring(
            archive.read("Metadata/model_settings.config")
        )
        plate = json.loads(archive.read("Metadata/plate_1.json"))
        project_settings = json.loads(
            archive.read("Metadata/project_settings.config")
        )
        names = [
            node.find("./metadata[@key='name']").attrib["value"]
            for node in settings.findall("object")
        ]
    report = {
        "dimensions_mm": {
            "straight_bore_diameter": 6.60,
            "bed_face_mouth_diameter": 7.00,
            "entrance_flare_height": 0.70,
            "pocket_depth": 4.55,
            "magnet": [6.0, 2.0],
            "insulating_skin": 0.30,
            "target_magnetic_gap": 0.35,
            "boss_outer_diameter": 8.60,
            "nominal_radial_wall": 1.00,
            "screw_head_clearance_diameter": 5.60,
        },
        "clearance_analysis": {
            "boss_radius_increase": 0.30,
            "nearest_front_locator_plan_gap": 0.20,
            "nearest_rear_locator_plan_gap": 1.20,
            "boss_height_unchanged": 6.80,
            "result": (
                "The boss expands only 0.30 mm radially at the existing PCB "
                "mounting pads. It remains inside the drawer envelope, below "
                "the unchanged PCB mount plane, clear of locators, rails, "
                "detents, neighboring pockets, and chassis walls."
            ),
        },
        "slices": {
            key: {
                "totals": estimates[key]["totals"],
                "warning_message": estimates[key]["plates"][0][
                    "warning_message"
                ],
                "maximum_bridge_mm": bridges[key][
                    "maximum_observed_span_mm"
                ],
            }
            for key in estimates
        },
        "combined_project": {
            "objects": names,
            "bbox_objects": plate["bbox_objects"],
            "supports_enabled": project_settings.get("enable_support"),
            "crc_valid": crc_valid,
            "embedded_gcode_md5_valid": (
                hashlib.md5(gcode, usedforsecurity=False).hexdigest()
                == expected_md5
            ),
            "sha256": digest(project),
        },
        "native_reopen_reslice": reopen,
        "replacement_hashes": {
            path.name: digest(path)
            for path in [
                package / "05_Pi_Drawer_1_6mm_Magnet_Fit.stl",
                package / "06_Pi_Drawer_2_6mm_Magnet_Fit.stl",
                package / "pi_magnet_pocket_6mm_section.png",
            ]
        },
        "protected_hashes": {
            relative: {
                "sha256": digest(ROOT / relative),
                "unchanged": digest(ROOT / relative) == expected,
            }
            for relative, expected in PROTECTED.items()
        },
    }
    args.output.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
