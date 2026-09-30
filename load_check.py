"""Conservative PLA screening calculations for the rack geometry.

This is not finite-element analysis. It checks local honeycomb-web bending and
stack/side-key strength using deliberately pessimistic load sharing.
"""

# SPDX-License-Identifier: MIT

from math import pi, sqrt

GRAVITY = 9.81  # m/s^2
DESIGN_MASS_KG = 1.0
SHOCK_FACTOR = 2.0
PLA_MODULUS_MPA = 3000.0
PLA_YIELD_MPA = 45.0
PLA_SHEAR_MPA = 30.0

CELL_RADIUS_MM = 11.0
HOLE_RADIUS_MM = 8.9
BASE_HEIGHT_MM = 1.8
PEG_DIAMETER_MM = 4.4
PEG_COUNT = 4
SIDE_KEY_ROOT_MM = 7.2
SIDE_KEY_LENGTH_MM = 3.2
SIDE_KEY_COUNT = 4
SIDE_KEY_INTERLAYER_ALLOWABLE_MPA = 8.0
SIDE_TOWER_WIDTH_MM = 8.0
SIDE_TOWER_DEPTH_MM = 14.0
SIDE_TOWER_COUNT = 2
SIDE_TOWER_LOAD_HEIGHT_MM = 33.0
LOAD_SHARING_WEBS = 8

span_mm = sqrt(3) * CELL_RADIUS_MM
web_width_mm = span_mm - 2 * HOLE_RADIUS_MM
design_force_n = DESIGN_MASS_KG * GRAVITY * SHOCK_FACTOR
web_force_n = design_force_n / LOAD_SHARING_WEBS

inertia_mm4 = web_width_mm * BASE_HEIGHT_MM**3 / 12
moment_nmm = web_force_n * span_mm / 4
web_stress_mpa = moment_nmm * (BASE_HEIGHT_MM / 2) / inertia_mm4
web_deflection_mm = (
    web_force_n
    * span_mm**3
    / (48 * PLA_MODULUS_MPA * inertia_mm4)
)
web_safety = PLA_YIELD_MPA / web_stress_mpa

peg_area_mm2 = PEG_COUNT * pi * PEG_DIAMETER_MM**2 / 4
peg_shear_mpa = design_force_n / peg_area_mm2
peg_safety = PLA_SHEAR_MPA / peg_shear_mpa

side_key_area_mm2 = (
    SIDE_KEY_COUNT * SIDE_KEY_ROOT_MM**2 / 2
)
side_key_shear_mpa = design_force_n / side_key_area_mm2
side_key_shear_safety = PLA_SHEAR_MPA / side_key_shear_mpa

# Treat every key as a short cantilever sharing a 2g vertical seam load.
# A diamond with equal diagonals d has section modulus d^3 / 24.
side_key_force_n = design_force_n / SIDE_KEY_COUNT
side_key_moment_nmm = side_key_force_n * SIDE_KEY_LENGTH_MM
side_key_section_mm3 = SIDE_KEY_ROOT_MM**3 / 24
side_key_bending_mpa = side_key_moment_nmm / side_key_section_mm3
side_key_bending_safety = (
    SIDE_KEY_INTERLAYER_ALLOWABLE_MPA / side_key_bending_mpa
)

# Conservatively ignore the 45-degree floor buttress and let two solid tower
# roots share the full lateral shock load at the upper key height.
side_tower_force_n = design_force_n / SIDE_TOWER_COUNT
side_tower_moment_nmm = (
    side_tower_force_n * SIDE_TOWER_LOAD_HEIGHT_MM
)
side_tower_section_mm3 = (
    SIDE_TOWER_DEPTH_MM * SIDE_TOWER_WIDTH_MM**2 / 6
)
side_tower_bending_mpa = (
    side_tower_moment_nmm / side_tower_section_mm3
)
side_tower_bending_safety = (
    SIDE_KEY_INTERLAYER_ALLOWABLE_MPA / side_tower_bending_mpa
)

print(f"Design load: {design_force_n:.2f} N (1 kg at 2g)")
print(f"Minimum honeycomb web: {web_width_mm:.2f} mm")
print(f"Screened web bending stress: {web_stress_mpa:.2f} MPa")
print(f"Screened web deflection: {web_deflection_mm:.3f} mm")
print(f"Web yield safety factor: {web_safety:.2f}")
print(f"Four-peg shear stress: {peg_shear_mpa:.3f} MPa")
print(f"Peg shear safety factor: {peg_safety:.1f}")
print(f"Side-key shear stress: {side_key_shear_mpa:.3f} MPa")
print(f"Side-key shear safety factor: {side_key_shear_safety:.1f}")
print(f"Side-key root bending stress: {side_key_bending_mpa:.2f} MPa")
print(
    "Side-key interlayer bending safety factor: "
    f"{side_key_bending_safety:.1f}"
)
print(
    "Side-tower root bending stress: "
    f"{side_tower_bending_mpa:.2f} MPa"
)
print(
    "Side-tower interlayer bending safety factor: "
    f"{side_tower_bending_safety:.1f}"
)

if (
    web_safety < 2.0
    or peg_safety < 3.0
    or side_key_shear_safety < 3.0
    or side_key_bending_safety < 3.0
    or side_tower_bending_safety < 3.0
):
    raise SystemExit("Screening safety factor is below the configured limit.")
