"""Validate the tracked release package without requiring slicer workspaces."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import hashlib
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

import trimesh


ROOT = Path(__file__).resolve().parent
PRODUCTION = [
    "01_UCG_Ultra.stl",
    "02_USW_Ultra_Left.stl",
    "03_USW_Ultra_Right.stl",
    "04_Dual_Pi_Chassis.stl",
    "05_Pi_Drawer_1.stl",
    "06_Pi_Drawer_2.stl",
    "07_Vent_Insert.stl",
    "08_UK_Ultra_Top.stl",
    "09_Rear_Spine_A.stl",
    "10_Rear_Spine_B.stl",
]
TEST_FIRST = [
    "01_Bay_Fit_Test.stl",
    "02_Rear_Spine_A.stl",
    "03_Rear_Spine_B.stl",
    "04_Desktop_Feet_Set.stl",
    "05_Magnet_Keystone_Peg_Test.stl",
    "06_Vent_Insert.stl",
    "07_Magnet_Polarity_Key.stl",
    "08_Rack_Ear_Test.stl",
    "09_Seam_Tower_Male_Test.stl",
    "10_Seam_Tower_Female_Test.stl",
]
EXPECTED_TOTALS = {
    "grams": 547.11,
    "length_m": 183.43948,
    "volume_cm3": 441.22368,
    "serial_seconds": 89031,
}
NO_TEST_TOTALS = {
    "beds": 5,
    "grams": 517.58,
    "length_m": 173.53468,
    "volume_cm3": 417.39985,
    "serial_seconds": 83599,
}
NO_SUPPORT_TOTALS = {
    "beds": 5,
    "grams": 516.7,
    "length_m": 173.23944,
    "volume_cm3": 416.68971,
    "serial_seconds": 83216,
}
NO_TEST_PLATES = [
    {"01_UCG_Ultra.stl", "09_Rear_Spine_A.stl"},
    {"02_USW_Ultra_Left.stl", "10_Rear_Spine_B.stl"},
    {"04_Dual_Pi_Chassis.stl", "07_Vent_Insert.stl"},
    {"03_USW_Ultra_Right.stl", "06_Pi_Drawer_2.stl"},
    {
        "08_UK_Ultra_Top.stl",
        "05_Pi_Drawer_1.stl",
        "04_Desktop_Feet_Set.stl",
    },
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_mesh(path: Path) -> None:
    loaded = trimesh.load_mesh(path, process=False)
    mesh = loaded.to_geometry() if isinstance(loaded, trimesh.Scene) else loaded
    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError(f"{path.relative_to(ROOT)} is not a triangle mesh")
    mesh = mesh.copy()
    mesh.merge_vertices()
    mesh.remove_unreferenced_vertices()
    bodies = len(mesh.split(only_watertight=False))
    minimum = mesh.bounds[0]
    size = mesh.extents
    if not mesh.is_watertight or bodies != 1:
        raise ValueError(
            f"{path.relative_to(ROOT)}: watertight={mesh.is_watertight}, bodies={bodies}"
        )
    if abs(float(minimum[2])) > 0.001:
        raise ValueError(f"{path.relative_to(ROOT)} is not on the print bed")
    if any(float(value) > 256.001 for value in size):
        raise ValueError(f"{path.relative_to(ROOT)} exceeds the A1 build volume")
    print(
        f"OK {path.relative_to(ROOT)} "
        f"({size[0]:.2f} x {size[1]:.2f} x {size[2]:.2f} mm)"
    )


def check_no_test_project(path: Path, targeted_supports: bool) -> None:
    with ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError("No-test 3MF has a CRC failure")
        settings = ET.fromstring(
            archive.read("Metadata/model_settings.config")
        )
        names = {
            node.attrib["id"]: node.find(
                "./metadata[@key='name']"
            ).attrib["value"]
            for node in settings.findall("object")
        }
        actual_plates = []
        for plate in settings.findall("plate"):
            actual_plates.append(
                {
                    names[
                        instance.find(
                            "./metadata[@key='object_id']"
                        ).attrib["value"]
                    ]
                    for instance in plate.findall("model_instance")
                }
            )
        if actual_plates != NO_TEST_PLATES:
            raise ValueError(
                f"Unexpected no-test plate inventory: {actual_plates}"
            )
        flattened = [name for plate in actual_plates for name in plate]
        if len(flattened) != len(set(flattened)) or len(flattened) != 11:
            raise ValueError("No-test project has duplicate or missing objects")
        enforcers = [
            part
            for node in settings.findall("object")
            for part in node.findall("part")
            if part.attrib.get("subtype") == "support_enforcer"
        ]
        expected_enforcers = 1 if targeted_supports else 0
        if len(enforcers) != expected_enforcers:
            raise ValueError(
                f"Expected {expected_enforcers} support enforcers, "
                f"found {len(enforcers)}"
            )

        for index in range(1, 6):
            plate_json = json.loads(
                archive.read(f"Metadata/plate_{index}.json")
            )
            boxes = [item["bbox"] for item in plate_json["bbox_objects"]]
            for box in boxes:
                if min(box) < 0 or max(box) > 256:
                    raise ValueError(
                        f"No-test plate {index} exceeds the A1 bed"
                    )
            for left_index, left in enumerate(boxes):
                for right in boxes[left_index + 1 :]:
                    separated = (
                        left[2] < right[0]
                        or right[2] < left[0]
                        or left[3] < right[1]
                        or right[3] < left[1]
                    )
                    if not separated:
                        raise ValueError(
                            f"No-test plate {index} has overlapping bboxes"
                        )

            gcode_name = f"Metadata/plate_{index}.gcode"
            md5_name = f"{gcode_name}.md5"
            expected = archive.read(md5_name).decode("ascii").strip().lower()
            actual = hashlib.md5(
                archive.read(gcode_name), usedforsecurity=False
            ).hexdigest()
            if actual != expected:
                raise ValueError(f"Embedded G-code MD5 mismatch: plate {index}")
            has_support_paths = (
                b"; FEATURE: Support" in archive.read(gcode_name)
            )
            expected_support_paths = targeted_supports and index == 1
            if has_support_paths != expected_support_paths:
                raise ValueError(
                    f"Unexpected support toolpaths on plate {index}"
                )

        core = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
        model = ET.fromstring(archive.read("3D/3dmodel.model"))
        for item in model.findall(f".//{{{core}}}build/{{{core}}}item"):
            values = [float(value) for value in item.attrib["transform"].split()]
            if (
                len(values) != 12
                or any(abs(values[index]) > 1e-8 for index in (2, 5, 6, 7))
                or abs(values[8] - 1) > 1e-8
                or not math.isclose(
                    abs(values[0] * values[4] - values[1] * values[3]),
                    1,
                    abs_tol=1e-6,
                )
            ):
                raise ValueError("No-test project tips an object off its validated face")

        project = json.loads(
            archive.read("Metadata/project_settings.config")
        )
        expected_settings = {
            "enable_support": "1" if targeted_supports else "0",
            "brim_type": "no_brim",
            "skirt_loops": "0",
            "wall_loops": "4",
            "sparse_infill_density": "20%",
            "sparse_infill_pattern": "gyroid",
            "top_shell_layers": "5",
            "bottom_shell_layers": "4",
        }
        if targeted_supports:
            expected_settings.update(
                {
                    "support_type": "normal(manual)",
                    "support_on_build_plate_only": "0",
                }
            )
        for key, value in expected_settings.items():
            if project.get(key) != value:
                raise ValueError(f"Unexpected no-test setting {key}")


def main() -> None:
    production_dir = ROOT / "PRINT_THESE" / "STLs"
    test_dir = ROOT / "PRINT_THESE" / "TEST_FIRST"
    for name in PRODUCTION:
        path = production_dir / name
        check_mesh(path)
        viewer = ROOT / "viewer" / "public" / "models" / name
        if digest(path) != digest(viewer):
            raise ValueError(f"Viewer copy differs from {path.relative_to(ROOT)}")
    for name in TEST_FIRST:
        check_mesh(test_dir / name)

    estimate_path = ROOT / "slicer" / "release" / "estimate.json"
    viewer_estimate = ROOT / "viewer" / "public" / "estimate.json"
    if digest(estimate_path) != digest(viewer_estimate):
        raise ValueError("Viewer estimate is not synchronized with slicer estimate")
    totals = json.loads(estimate_path.read_text(encoding="utf-8"))["totals"]
    for key, expected in EXPECTED_TOTALS.items():
        if totals[key] != expected:
            raise ValueError(f"Unexpected release total {key}: {totals[key]}")

    no_test_project = (
        ROOT
        / "PRINT_THESE"
        / "homelab-rack-Bambu-Studio-5-plates-NO-TEST.3mf"
    )
    check_no_test_project(no_test_project, targeted_supports=True)
    no_support_project = (
        ROOT
        / "PRINT_THESE"
        / "homelab-rack-Bambu-Studio-5-plates-NO-TEST-NO-SUPPORT.3mf"
    )
    check_no_test_project(no_support_project, targeted_supports=False)
    no_test_audit = json.loads(
        (ROOT / "PRINT_THESE" / "NO_TEST_BAMBU_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    if no_test_audit["project_sha256"] != digest(no_test_project):
        raise ValueError("No-test project audit is not synchronized")
    no_test_estimate = json.loads(
        (ROOT / "slicer" / "release" / "no-test-estimate.json").read_text(
            encoding="utf-8"
        )
    )
    for key, expected in NO_TEST_TOTALS.items():
        if no_test_estimate["totals"][key] != expected:
            raise ValueError(
                f"Unexpected no-test release total {key}: "
                f"{no_test_estimate['totals'][key]}"
            )
    no_support_estimate = json.loads(
        (
            ROOT
            / "slicer"
            / "release"
            / "no-test-no-support-estimate.json"
        ).read_text(encoding="utf-8")
    )
    for key, expected in NO_SUPPORT_TOTALS.items():
        if no_support_estimate["totals"][key] != expected:
            raise ValueError(
                f"Unexpected no-support total {key}: "
                f"{no_support_estimate['totals'][key]}"
            )
    support_ab = json.loads(
        (
            ROOT / "slicer" / "release" / "no-test-support-ab-audit.json"
        ).read_text(encoding="utf-8")
    )
    if support_ab["totals"]["support_delta_grams"] != 0.88:
        raise ValueError("Unexpected targeted-support material delta")
    supported_plates = [
        plate["plate"]
        for plate in support_ab["plates"]
        if plate["targeted"]["support_toolpaths"]["segments"] > 0
    ]
    if supported_plates != [1]:
        raise ValueError(
            f"Unexpected targeted-support plates: {supported_plates}"
        )
    bridge = json.loads(
        (
            ROOT / "slicer" / "release" / "no-test-bridge-audit.json"
        ).read_text(encoding="utf-8")
    )
    if bridge["maximum_observed_span_mm"] > 20:
        raise ValueError("No-test project exceeds the 20 mm bridge gate")

    required = [
        ROOT / "PRINT_THESE" / "homelab-rack-Bambu-Studio-6-plates.3mf",
        no_test_project,
        no_support_project,
        ROOT / "PRINT_THESE" / "NO_TEST_BAMBU_AUDIT.json",
        ROOT / "slicer" / "release" / "no-test-support-ab-audit.json",
        ROOT / "renders" / "supports-no-test" / "support_plate_1.png",
        test_dir / "plate_1-test.3mf",
        ROOT / "LICENSES" / "CERN-OHL-S-2.0.txt",
        ROOT / "LICENSES" / "MIT.txt",
        ROOT / "LICENSES" / "CC-BY-4.0.txt",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing release files: {', '.join(missing)}")

    print(
        "Release package verified: 20 printable STLs, 10 viewer copies, "
        "pinned totals, four Bambu projects, and three license texts."
    )


if __name__ == "__main__":
    main()
