"""Validate the tracked release package without requiring slicer workspaces."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import hashlib
import json
from pathlib import Path

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
    "grams": 529.43,
    "length_m": 177.51018,
    "volume_cm3": 426.96198,
    "serial_seconds": 83062,
}


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

    required = [
        ROOT / "PRINT_THESE" / "homelab-rack-Bambu-Studio-6-plates.3mf",
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
        "pinned totals, two Bambu projects, and three license texts."
    )


if __name__ == "__main__":
    main()
