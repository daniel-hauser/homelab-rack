"""Validate the isolated Pi HAT clearance replacement package."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import hashlib
import json
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parent
PACKAGE = (
    ROOT
    / "PRINT_THESE"
    / "REPLACEMENTS"
    / "PI-HAT-5MM-CLEARANCE"
)
STL = PACKAGE / "04_Dual_Pi_Chassis_5mm_HAT_Clearance.stl"
PROJECT = PACKAGE / "homelab-rack-Dual-Pi-Chassis-5mm-HAT-Clearance.3mf"
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
NUMBER = r"-?(?:\d+(?:\.\d*)?|\.\d+)"
VALUE = re.compile(rf"([XYZE])({NUMBER})")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def vertical_hits(
    mesh: trimesh.Trimesh, x: float, y: float
) -> list[float]:
    hits = []
    for triangle in mesh.triangles:
        first, second, third = triangle
        matrix = np.array(
            [
                [second[0] - first[0], third[0] - first[0]],
                [second[1] - first[1], third[1] - first[1]],
            ]
        )
        determinant = float(np.linalg.det(matrix))
        if abs(determinant) < 1e-10:
            continue
        u, v = np.linalg.solve(
            matrix, np.array([x - first[0], y - first[1]])
        )
        if u >= -1e-8 and v >= -1e-8 and u + v <= 1 + 1e-8:
            hits.append(
                float(
                    first[2]
                    + u * (second[2] - first[2])
                    + v * (third[2] - first[2])
                )
            )
    unique = []
    for value in sorted(hits):
        if not unique or abs(value - unique[-1]) > 1e-5:
            unique.append(value)
    return [round(value, 3) for value in unique]


def support_distribution(gcode: bytes) -> dict[str, int]:
    feature = ""
    x: float | None = None
    y: float | None = None
    counts = {"left": 0, "center": 0, "right": 0, "outside_front": 0}
    for line in gcode.decode("utf-8", errors="ignore").splitlines():
        if line.startswith("; FEATURE:"):
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
            and math.hypot(next_x - x, next_y - y) > 0.01
        ):
            midpoint_x = (x + next_x) / 2
            midpoint_y = (y + next_y) / 2
            if midpoint_x < 95:
                counts["left"] += 1
            elif midpoint_x > 160:
                counts["right"] += 1
            else:
                counts["center"] += 1
            if not 51 <= midpoint_y <= 61:
                counts["outside_front"] += 1
        x, y = next_x, next_y
    return counts


def check() -> None:
    for relative, expected in EXPECTED_PROTECTED.items():
        actual = digest(ROOT / relative)
        if actual != expected:
            raise ValueError(f"Protected artifact changed: {relative}")

    loaded = trimesh.load_mesh(STL, process=True)
    mesh = loaded.to_geometry() if isinstance(loaded, trimesh.Scene) else loaded
    if not mesh.is_watertight or len(mesh.split()) != 1:
        raise ValueError("Replacement STL is not one watertight body")
    if not np.allclose(mesh.extents, [244.5, 152.0, 46.7], atol=0.001):
        raise ValueError(f"Unexpected replacement extents: {mesh.extents}")
    if abs(float(mesh.bounds[0][2])) > 0.001:
        raise ValueError("Replacement STL is not on the print bed")
    expected_front = {
        54.65: [0.0, 6.0, 41.0, 43.7],
        120.65: [0.0, 6.0, 36.0, 43.7],
        186.65: [0.0, 6.0, 41.0, 43.7],
    }
    for x, expected in expected_front.items():
        actual = vertical_hits(mesh, x, 1.5)
        if actual != expected:
            raise ValueError(f"Unexpected front opening at X={x}: {actual}")
    for x in expected_front:
        if vertical_hits(mesh, x, 60.0) != [0.0, 1.8]:
            raise ValueError(f"Hidden roof or rib found behind bay X={x}")

    with ZipFile(PROJECT) as archive:
        if archive.testzip() is not None:
            raise ValueError("Replacement 3MF has a CRC failure")
        settings = ET.fromstring(
            archive.read("Metadata/model_settings.config")
        )
        names = [
            node.find("./metadata[@key='name']").attrib["value"]
            for node in settings.findall("object")
        ]
        if names != ["04_Dual_Pi_Chassis_5mm_HAT_Clearance.stl"]:
            raise ValueError(f"Unexpected replacement project objects: {names}")
        enforcers = [
            part
            for part in settings.findall(".//part")
            if part.attrib.get("subtype") == "support_enforcer"
        ]
        if len(enforcers) != 2:
            raise ValueError("Replacement project must have two enforcers")
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
                raise ValueError(f"Unexpected replacement setting {key}")
        gcode = archive.read("Metadata/plate_1.gcode")
        expected_md5 = archive.read(
            "Metadata/plate_1.gcode.md5"
        ).decode("ascii").strip().lower()
        if hashlib.md5(gcode, usedforsecurity=False).hexdigest() != expected_md5:
            raise ValueError("Replacement embedded G-code MD5 mismatch")
        distribution = support_distribution(gcode)
        if (
            distribution["left"] == 0
            or distribution["right"] == 0
            or distribution["center"] != 0
            or distribution["outside_front"] != 0
        ):
            raise ValueError(
                f"Unexpected replacement support distribution: {distribution}"
            )
        plate = json.loads(archive.read("Metadata/plate_1.json"))
        box = plate["bbox_objects"][0]["bbox"]
        if min(box) < 0 or max(box) > 256:
            raise ValueError("Replacement project exceeds the A1 bed")

    estimate = json.loads(
        (PACKAGE / "slice-estimate.json").read_text(encoding="utf-8")
    )
    if estimate["totals"] != {
        "beds": 1,
        "grams": 113.22,
        "length_m": 37.96089,
        "volume_cm3": 91.30664,
        "serial_seconds": 17434,
        "serial_time": "4h50m34s",
    }:
        raise ValueError("Unexpected replacement slice totals")
    audit = json.loads(
        (PACKAGE / "PI_HAT_5MM_CLEARANCE_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    if (
        audit["opening_heights_mm"] != [35.0, 30.0, 35.0]
        or audit["remaining_top_rail_mm"] != 2.7
        or audit["delta"] != {"grams": 6.1, "seconds": 837}
        or audit["baseline"]["overhang_walls"][
            "raised_front_rail_segments"
        ]["maximum_mm"] != 61.6
    ):
        raise ValueError("Replacement A/B audit is inconsistent")

    required = [
        PACKAGE / "README.txt",
        PACKAGE / "pi_hat_5mm_clearance_front_cutaway.png",
        PACKAGE / "support_toolpaths.png",
        PACKAGE / "bridge-audit.json",
        PACKAGE / "no-support-bridge-audit.json",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing replacement evidence: {missing}")
    print(
        "Replacement verified: 35/30/35 mm openings, 2.7 mm rails, "
        "two front-only supports, protected hashes unchanged."
    )


if __name__ == "__main__":
    check()
