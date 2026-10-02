"""Validate the isolated 6 mm magnet-fit Pi drawer replacement package."""

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

from slicer.pi_magnet_replacement_audit import PROTECTED


ROOT = Path(__file__).resolve().parent
PACKAGE = (
    ROOT
    / "PRINT_THESE"
    / "REPLACEMENTS"
    / "PI-MAGNET-POCKET-6MM"
)
DRAWERS = [
    PACKAGE / "05_Pi_Drawer_1_6mm_Magnet_Fit.stl",
    PACKAGE / "06_Pi_Drawer_2_6mm_Magnet_Fit.stl",
]
PROJECT = PACKAGE / "homelab-rack-Pi-Drawers-6mm-Magnet-Fit.3mf"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def horizontal_hits(
    mesh: trimesh.Trimesh, y: float, z: float
) -> list[float]:
    hits = []
    for triangle in mesh.triangles:
        first, second, third = triangle
        matrix = np.array(
            [
                [second[1] - first[1], third[1] - first[1]],
                [second[2] - first[2], third[2] - first[2]],
            ]
        )
        determinant = float(np.linalg.det(matrix))
        if abs(determinant) < 1e-10:
            continue
        u, v = np.linalg.solve(
            matrix, np.array([y - first[1], z - first[2]])
        )
        if u >= -1e-8 and v >= -1e-8 and u + v <= 1 + 1e-8:
            hits.append(
                float(
                    first[0]
                    + u * (second[0] - first[0])
                    + v * (third[0] - first[0])
                )
            )
    unique = []
    for value in sorted(hits):
        if not unique or abs(value - unique[-1]) > 1e-5:
            unique.append(value)
    return [round(value, 4) for value in unique]


def near_center(values: list[float], center: float) -> list[float]:
    return [value for value in values if abs(value - center) < 5]


def check_pockets(mesh: trimesh.Trimesh) -> None:
    for y in [28.9, 86.9]:
        for center in [7.75, 56.75]:
            mouth = near_center(horizontal_hits(mesh, y, 0.01), center)
            bore = near_center(horizontal_hits(mesh, y, 0.70), center)
            wall = near_center(horizontal_hits(mesh, y, 2.00), center)
            pocket_top = near_center(
                horizontal_hits(mesh, y, 4.559), center
            )
            skin = near_center(horizontal_hits(mesh, y, 4.561), center)
            roof = near_center(horizontal_hits(mesh, y, 4.70), center)
            screw = near_center(horizontal_hits(mesh, y, 4.86), center)
            if len(mouth) != 2 or not math.isclose(
                mouth[1] - mouth[0], 6.9888, abs_tol=0.02
            ):
                raise ValueError(f"Unexpected flared mouth at {center}, {y}")
            if len(bore) != 2 or not math.isclose(
                bore[1] - bore[0], 6.60, abs_tol=0.01
            ):
                raise ValueError(f"Unexpected straight bore at {center}, {y}")
            visible_wall = (
                wall[1] - wall[0]
                if center < 32
                else wall[2] - wall[1]
            )
            if len(wall) != 3 or not math.isclose(
                visible_wall, 1.0, abs_tol=0.01
            ):
                raise ValueError(f"Unexpected boss wall at {center}, {y}")
            if len(pocket_top) != 4 or len(skin) != 2:
                raise ValueError(
                    f"Unexpected pocket depth or skin at {center}, {y}"
                )
            if len(roof) != 2 or not math.isclose(
                roof[1] - roof[0], 8.60, abs_tol=0.01
            ):
                raise ValueError(f"Insulating roof is open at {center}, {y}")
            if len(screw) != 4 or not math.isclose(
                screw[2] - screw[1], 5.60, abs_tol=0.01
            ):
                raise ValueError(
                    f"Unexpected screw-head clearance at {center}, {y}"
                )


def check() -> None:
    for relative, expected in PROTECTED.items():
        if digest(ROOT / relative) != expected:
            raise ValueError(f"Protected artifact changed: {relative}")

    for path in DRAWERS:
        loaded = trimesh.load_mesh(path, process=True)
        mesh = (
            loaded.to_geometry()
            if isinstance(loaded, trimesh.Scene)
            else loaded
        )
        if not mesh.is_watertight or len(mesh.split()) != 1:
            raise ValueError(f"{path.name} is not one watertight body")
        if not np.allclose(
            mesh.extents, [64.5, 114.4, 30.0], atol=0.001
        ):
            raise ValueError(f"Unexpected drawer extents: {mesh.extents}")
        if abs(float(mesh.bounds[0][2])) > 0.001:
            raise ValueError(f"{path.name} is not on the print bed")
        check_pockets(mesh)

    with ZipFile(PROJECT) as archive:
        if archive.testzip() is not None:
            raise ValueError("Magnet replacement 3MF has a CRC failure")
        settings = ET.fromstring(
            archive.read("Metadata/model_settings.config")
        )
        names = [
            node.find("./metadata[@key='name']").attrib["value"]
            for node in settings.findall("object")
        ]
        expected_names = [
            "05_Pi_Drawer_1_6mm_Magnet_Fit.stl",
            "06_Pi_Drawer_2_6mm_Magnet_Fit.stl",
        ]
        if names != expected_names:
            raise ValueError(f"Unexpected replacement objects: {names}")
        project = json.loads(
            archive.read("Metadata/project_settings.config")
        )
        if project.get("enable_support") != "0":
            raise ValueError("Magnet replacement must remain support-free")
        gcode = archive.read("Metadata/plate_1.gcode")
        if b"; FEATURE: Support" in gcode:
            raise ValueError("Magnet replacement contains support toolpaths")
        expected_md5 = archive.read(
            "Metadata/plate_1.gcode.md5"
        ).decode("ascii").strip().lower()
        if hashlib.md5(gcode, usedforsecurity=False).hexdigest() != expected_md5:
            raise ValueError("Magnet replacement embedded G-code MD5 mismatch")
        plate = json.loads(archive.read("Metadata/plate_1.json"))
        boxes = [item["bbox"] for item in plate["bbox_objects"]]
        if any(min(box) < 0 or max(box) > 256 for box in boxes):
            raise ValueError("Magnet replacement exceeds the A1 bed")
        horizontal_gap = max(boxes[0][0], boxes[1][0]) - min(
            boxes[0][2], boxes[1][2]
        )
        if horizontal_gap < 4.0:
            raise ValueError(f"Drawer spacing is too small: {horizontal_gap}")

    audit = json.loads(
        (PACKAGE / "PI_MAGNET_POCKET_6MM_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    dimensions = audit["dimensions_mm"]
    expected_dimensions = {
        "straight_bore_diameter": 6.6,
        "bed_face_mouth_diameter": 7.0,
        "entrance_flare_height": 0.7,
        "pocket_depth": 4.55,
        "magnet": [6.0, 2.0],
        "insulating_skin": 0.3,
        "target_magnetic_gap": 0.35,
        "boss_outer_diameter": 8.6,
        "nominal_radial_wall": 1.0,
        "screw_head_clearance_diameter": 5.6,
    }
    if dimensions != expected_dimensions:
        raise ValueError("Magnet replacement dimensions are inconsistent")
    combined = audit["slices"]["combined"]
    if (
        combined["totals"]["grams"] != 30.32
        or combined["totals"]["serial_seconds"] != 6474
        or combined["maximum_bridge_mm"] != 6.32
        or combined["warning_message"]
    ):
        raise ValueError("Unexpected combined drawer slice audit")
    reopen = audit["native_reopen_reslice"]
    if not (
        reopen["reopened_project_crc_valid"]
        and reopen["embedded_gcode_md5_valid"]
        and reopen["totals"]["grams"] == 30.32
        and reopen["maximum_bridge_mm"] == 6.32
        and not reopen["warning_message"]
        and not reopen["support_toolpaths"]
        and reopen["difference_from_release_slice"]
        == {"grams": 0.0, "seconds": -9, "maximum_bridge_mm": 0.0}
    ):
        raise ValueError("Native reopen/reslice evidence is inconsistent")

    required = [
        PACKAGE / "README.txt",
        PACKAGE / "pi_magnet_pocket_6mm_section.png",
        PACKAGE / "drawer-1-estimate.json",
        PACKAGE / "drawer-2-estimate.json",
        PACKAGE / "bridge-audit.json",
    ]
    missing = [
        str(path.relative_to(ROOT))
        for path in required
        if not path.is_file()
    ]
    if missing:
        raise FileNotFoundError(f"Missing magnet replacement evidence: {missing}")
    print(
        "Magnet replacement verified: 6.60 mm bores, 7.00 mm mouths, "
        "0.70 mm flares, 1.00 mm boss walls, protected hashes unchanged."
    )


if __name__ == "__main__":
    check()
