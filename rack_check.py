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

print(f"Paired width: {RACK_WIDTH_MM:.2f} mm")
print(f"Half width: {HALF_WIDTH_MM:.2f} mm")
print(f"Horizontal mounting centers: {paired_spacing:.2f} mm")
print(
    "Vertical centers: "
    + ", ".join(f"{value:.3f}" for value in VERTICAL_CENTERS_MM)
    + " mm"
)
print(f"Printed mounting slots: {SLOT_WIDTH_MM:.1f} x {SLOT_HEIGHT_MM:.1f} mm")
