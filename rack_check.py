"""Verify the paired ear geometry against the EIA-310 19-inch pattern."""

# SPDX-License-Identifier: MIT

from math import isclose

RACK_WIDTH_MM = 482.60
HORIZONTAL_CENTERS_MM = 465.10
U_HEIGHT_MM = 44.45
HALF_WIDTH_MM = RACK_WIDTH_MM / 2
OUTER_HOLE_CENTER_MM = (RACK_WIDTH_MM - HORIZONTAL_CENTERS_MM) / 2
VERTICAL_CENTERS_MM = (6.35, 22.225, 38.10)
SLOT_WIDTH_MM = 7.0
SLOT_HEIGHT_MM = 10.0
SIDE_KEY_PROTRUSION_MM = 3.2
SIDE_SOCKET_FACE_DEPTH_MM = 4.7
DESIGNED_SEAM_FACE_GAP_MM = 0.0
SIDE_SOCKET_AXIAL_RESERVE_MM = (
    SIDE_SOCKET_FACE_DEPTH_MM - SIDE_KEY_PROTRUSION_MM
)
BAY_OPENING_WIDTH_MM = 62.0
BAY_OPENING_HEIGHT_MM = 30.0
BAY_RECEIVING_CHAMFER_MM = 1.2
BAY_FRONT_WIDTH_MM = BAY_OPENING_WIDTH_MM + 2 * BAY_RECEIVING_CHAMFER_MM
BAY_FRONT_HEIGHT_MM = BAY_OPENING_HEIGHT_MM + 2 * BAY_RECEIVING_CHAMFER_MM
PI_DRAWER_SHOULDER_MM = 1.2
PI_PCB_THICKNESS_MM = 1.6
PI_REPLACEMENT_SCREW_DELTA_MM = PI_DRAWER_SHOULDER_MM
PI_MAGNETIC_HEAD_PROTRUSION_MM = 1.6
PI_MAGNETIC_GAP_MM = 0.35
PI_MAGNETIC_SKIN_MM = 0.30
CARTRIDGE_DETENT_PROTRUSION_MM = 0.45
CARTRIDGE_DETENT_POCKET_DEPTH_MM = 0.65
CARTRIDGE_DETENT_DEPTH_RELIEF_MM = (
    CARTRIDGE_DETENT_POCKET_DEPTH_MM - CARTRIDGE_DETENT_PROTRUSION_MM
)
CARTRIDGE_DETENT_SLOPE_RUN_MM = 11.2
CARTRIDGE_DETENT_SLOPE_RISE_MM = 11.2
VENT_FACE_WIDTH_MM = 64.5
VENT_FACE_HEIGHT_MM = 30.0
VENT_CARTRIDGE_DEPTH_MM = 111.0
VENT_TRACK_ENGAGEMENT_MM = VENT_CARTRIDGE_DEPTH_MM - 34.0
VENT_REAR_STOP_CLEARANCE_MM = 2.0
VENT_RUNNER_SIDE_CLEARANCE_MM = 0.15
BAY_FIT_COUPON_DEPTH_MM = 50.0
BAY_FIT_COUPON_GUIDE_LENGTH_MM = BAY_FIT_COUPON_DEPTH_MM - 34.0

left_center = OUTER_HOLE_CENTER_MM
right_center = HALF_WIDTH_MM + (
    HALF_WIDTH_MM - OUTER_HOLE_CENTER_MM
)
paired_spacing = right_center - left_center

assert isclose(HALF_WIDTH_MM * 2, RACK_WIDTH_MM, abs_tol=1e-9)
assert isclose(paired_spacing, HORIZONTAL_CENTERS_MM, abs_tol=1e-9)
assert isclose(
    VERTICAL_CENTERS_MM[1] - VERTICAL_CENTERS_MM[0],
    15.875,
    abs_tol=1e-9,
)
assert isclose(
    VERTICAL_CENTERS_MM[2] - VERTICAL_CENTERS_MM[1],
    15.875,
    abs_tol=1e-9,
)
assert VERTICAL_CENTERS_MM[-1] < U_HEIGHT_MM
assert SLOT_WIDTH_MM >= 7.0
assert isclose(DESIGNED_SEAM_FACE_GAP_MM, 0.0, abs_tol=1e-9)
assert isclose(SIDE_SOCKET_AXIAL_RESERVE_MM, 1.5, abs_tol=1e-9)
assert isclose(BAY_FRONT_WIDTH_MM, 64.4, abs_tol=1e-9)
assert isclose(BAY_FRONT_HEIGHT_MM, 32.4, abs_tol=1e-9)
assert isclose(PI_REPLACEMENT_SCREW_DELTA_MM, 1.2, abs_tol=1e-9)
assert isclose(
    CARTRIDGE_DETENT_SLOPE_RUN_MM,
    CARTRIDGE_DETENT_SLOPE_RISE_MM,
    abs_tol=1e-9,
)
assert isclose(VENT_FACE_WIDTH_MM, 64.5, abs_tol=1e-9)
assert isclose(VENT_FACE_HEIGHT_MM, 30.0, abs_tol=1e-9)
assert isclose(VENT_TRACK_ENGAGEMENT_MM, 77.0, abs_tol=1e-9)
assert isclose(VENT_REAR_STOP_CLEARANCE_MM, 2.0, abs_tol=1e-9)
assert isclose(VENT_RUNNER_SIDE_CLEARANCE_MM, 0.15, abs_tol=1e-9)
assert isclose(CARTRIDGE_DETENT_DEPTH_RELIEF_MM, 0.20, abs_tol=1e-9)
assert isclose(BAY_FIT_COUPON_GUIDE_LENGTH_MM, 16.0, abs_tol=1e-9)

print(f"Paired width: {RACK_WIDTH_MM:.2f} mm")
print(f"Half width: {HALF_WIDTH_MM:.2f} mm")
print(f"Horizontal mounting centers: {paired_spacing:.2f} mm")
print(
    "Vertical centers: "
    + ", ".join(f"{value:.3f}" for value in VERTICAL_CENTERS_MM)
    + " mm"
)
print(f"Printed mounting slots: {SLOT_WIDTH_MM:.1f} x {SLOT_HEIGHT_MM:.1f} mm")
print(f"Designed seam face gap: {DESIGNED_SEAM_FACE_GAP_MM:.1f} mm")
print(
    "Side-key socket axial reserve: "
    f"{SIDE_SOCKET_AXIAL_RESERVE_MM:.1f} mm"
)
print(
    "Pi bay receiving chamfer: "
    f"{BAY_RECEIVING_CHAMFER_MM:.1f} mm deep at 45 degrees, "
    f"{BAY_FRONT_WIDTH_MM:.1f} x {BAY_FRONT_HEIGHT_MM:.1f} mm front mouth"
)
print(
    "Pi bay retained friction opening: "
    f"{BAY_OPENING_WIDTH_MM:.1f} x {BAY_OPENING_HEIGHT_MM:.1f} mm"
)
print(
    "Pi through-floor review stack: "
    f"{PI_DRAWER_SHOULDER_MM:.1f} mm printed shoulder + "
    f"{PI_PCB_THICKNESS_MM:.1f} mm PCB; replacement screw must be "
    f"existing under-head length + {PI_REPLACEMENT_SCREW_DELTA_MM:.1f} mm"
)
print(
    "Pi magnetic direction (physical gate pending): "
    f"{PI_MAGNETIC_HEAD_PROTRUSION_MM:.2f} mm assumed head protrusion, "
    f"{PI_MAGNETIC_GAP_MM:.2f} mm target gap, "
    f"{PI_MAGNETIC_SKIN_MM:.2f} mm insulating skin"
)
print(
    "Cartridge service detent: "
    f"{CARTRIDGE_DETENT_PROTRUSION_MM:.2f} mm local engagement into "
    f"{CARTRIDGE_DETENT_POCKET_DEPTH_MM:.2f} mm pockets, "
    f"{CARTRIDGE_DETENT_DEPTH_RELIEF_MM:.2f} mm depth relief, "
    "45-degree support-free spring rise"
)
print(
    "Vent track-guided cartridge: "
    f"{VENT_FACE_WIDTH_MM:.1f} x {VENT_FACE_HEIGHT_MM:.1f} mm face, "
    f"{VENT_CARTRIDGE_DEPTH_MM:.1f} mm runners, "
    f"{VENT_TRACK_ENGAGEMENT_MM:.1f} mm guide-lip engagement, "
    f"{VENT_REAR_STOP_CLEARANCE_MM:.1f} mm rear reserve, "
    f"{VENT_RUNNER_SIDE_CLEARANCE_MM:.2f} mm per-side guide clearance"
)
print(
    "Bay fit coupon: "
    f"{BAY_FIT_COUPON_DEPTH_MM:.1f} mm deep with "
    f"{BAY_FIT_COUPON_GUIDE_LENGTH_MM:.1f} mm of common guide-lip geometry"
)
