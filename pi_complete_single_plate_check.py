"""Validate the consolidated single-plate Pi replacement package."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

from slicer.pi_complete_single_plate_audit import (
    EXPECTED_OBJECTS,
    PROTECTED,
)


ROOT = Path(__file__).resolve().parent
PACKAGE = (
    ROOT
    / "PRINT_THESE"
    / "REPLACEMENTS"
    / "PI-COMPLETE-SINGLE-PLATE"
)
PROJECT = PACKAGE / "homelab-rack-Pi-Complete-Single-Plate-A1.3mf"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check() -> None:
    for relative, expected in PROTECTED.items():
        if digest(ROOT / relative) != expected:
            raise ValueError(f"Protected artifact changed: {relative}")

    required = [
        PROJECT,
        PACKAGE / "README.txt",
        PACKAGE / "slice-estimate.json",
        PACKAGE / "object-inventory.json",
        PACKAGE / "bridge-audit.json",
        PACKAGE / "support-audit.json",
        PACKAGE / "protected-hashes.json",
        PACKAGE / "PI_COMPLETE_SINGLE_PLATE_AUDIT.json",
        PACKAGE / "pi_complete_single_plate_bed.png",
        PACKAGE / "pi_complete_support_toolpaths.png",
    ]
    missing = [
        str(path.relative_to(ROOT))
        for path in required
        if not path.is_file()
    ]
    if missing:
        raise FileNotFoundError(f"Missing consolidated evidence: {missing}")

    with ZipFile(PROJECT) as archive:
        if archive.testzip() is not None:
            raise ValueError("Consolidated project has a CRC failure")
        settings = ET.fromstring(
            archive.read("Metadata/model_settings.config")
        )
        objects = settings.findall("object")
        names = [
            node.find("./metadata[@key='name']").attrib["value"]
            for node in objects
        ]
        if sorted(names) != sorted(EXPECTED_OBJECTS):
            raise ValueError(f"Unexpected consolidated objects: {names}")
        enforcers = {
            node.find("./metadata[@key='name']").attrib["value"]: [
                part
                for part in node.findall("part")
                if part.attrib.get("subtype") == "support_enforcer"
            ]
            for node in objects
        }
        if len(enforcers[EXPECTED_OBJECTS[0]]) != 2 or any(
            enforcers[name] for name in EXPECTED_OBJECTS[1:]
        ):
            raise ValueError("Support enforcers are not chassis-only")
        project = json.loads(
            archive.read("Metadata/project_settings.config")
        )
        expected_settings = {
            "enable_support": "1",
            "support_type": "normal(manual)",
            "support_on_build_plate_only": "1",
            "wall_loops": "4",
            "sparse_infill_density": "20%",
            "sparse_infill_pattern": "gyroid",
            "brim_type": "no_brim",
            "skirt_loops": "0",
        }
        for key, expected in expected_settings.items():
            if project.get(key) != expected:
                raise ValueError(f"Unexpected project setting {key}")
        gcode = archive.read("Metadata/plate_1.gcode")
        expected_md5 = archive.read(
            "Metadata/plate_1.gcode.md5"
        ).decode("ascii").strip().lower()
        if hashlib.md5(gcode, usedforsecurity=False).hexdigest() != expected_md5:
            raise ValueError("Consolidated embedded G-code MD5 mismatch")
        plate = json.loads(archive.read("Metadata/plate_1.json"))

    expected_boxes = {
        EXPECTED_OBJECTS[0]: [5.75, 10.0, 247.05, 162.0],
        EXPECTED_OBJECTS[1]: [10.0, 171.6, 124.4, 233.9],
        EXPECTED_OBJECTS[2]: [131.6, 171.6, 246.0, 233.9],
    }
    actual_boxes = {
        item["name"]: [round(value, 2) for value in item["bbox"]]
        for item in plate["bbox_objects"]
    }
    if actual_boxes != expected_boxes:
        raise ValueError(f"Unexpected consolidated layout: {actual_boxes}")
    if [round(value, 2) for value in plate["bbox_all"]] != [
        5.75,
        10.0,
        247.05,
        233.9,
    ]:
        raise ValueError("Consolidated layout exceeds validated A1 bounds")

    inventory = json.loads(
        (PACKAGE / "object-inventory.json").read_text(encoding="utf-8")
    )
    if inventory["object_names"] != EXPECTED_OBJECTS:
        raise ValueError("Object inventory is inconsistent")
    if any(
        clearance["overlap"]
        for clearance in inventory["pairwise_clearances"]
    ):
        raise ValueError("Consolidated objects overlap")
    if inventory["bed_margins_mm"] != {
        "left": 5.75,
        "bottom": 10.0,
        "right": 8.95,
        "top": 22.1,
    }:
        raise ValueError("Unexpected consolidated bed margins")

    estimate = json.loads(
        (PACKAGE / "slice-estimate.json").read_text(encoding="utf-8")
    )
    if estimate["totals"] != {
        "beds": 1,
        "grams": 143.52,
        "length_m": 48.118610000000004,
        "volume_cm3": 115.73882,
        "serial_seconds": 23252,
        "serial_time": "6h27m32s",
    }:
        raise ValueError("Unexpected consolidated slice estimate")
    if estimate["plates"][0]["warning_message"]:
        raise ValueError("Consolidated slice contains a warning")

    bridge = json.loads(
        (PACKAGE / "bridge-audit.json").read_text(encoding="utf-8")
    )
    if bridge["maximum_observed_span_mm"] != 17.52:
        raise ValueError("Consolidated bridge gate changed")

    support = json.loads(
        (PACKAGE / "support-audit.json").read_text(encoding="utf-8")
    )
    if (
        support["segments"] != 3066
        or support["path_mm"] != 49273.94
        or support["bbox_mm"] != [26.05, 9.76, 224.24, 17.65]
        or support["regions"]["left"] == 0
        or support["regions"]["right"] == 0
        or support["regions"]["center"] != 0
        or support["drawers_receive_support"]
    ):
        raise ValueError("Consolidated support locality changed")

    audit = json.loads(
        (PACKAGE / "PI_COMPLETE_SINGLE_PLATE_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    reopen = audit["native_reopen_reslice"]
    if not (
        audit["project_integrity"]["zip_crc_valid"]
        and audit["project_integrity"]["embedded_gcode_md5_valid"]
        and reopen["zip_crc_valid"]
        and reopen["embedded_gcode_md5_valid"]
        and reopen["totals"]["grams"] == 143.52
        and reopen["totals"]["serial_seconds"] == 23239
        and reopen["maximum_bridge_mm"] == 17.52
        and not reopen["warning_message"]
        and reopen["difference_from_release_slice"]
        == {"grams": 0.0, "seconds": -13, "maximum_bridge_mm": 0.0}
        and reopen["support_toolpaths"]
        == {
            "segments": 3066,
            "path_mm": 49273.94,
            "layers": [1, 323],
            "bbox_mm": [26.05, 9.76, 224.24, 17.65],
            "regions": {"left": 1708, "center": 0, "right": 1358},
        }
    ):
        raise ValueError("Consolidated reopen/reslice evidence changed")
    print(
        "Consolidated Pi plate verified: three objects, chassis-only "
        "front-rail supports, no overlap, protected hashes unchanged."
    )


if __name__ == "__main__":
    check()
