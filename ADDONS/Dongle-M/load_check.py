"""Conservative static screening for the Dongle-M add-on."""

from math import pi

g = 9.81
mass_kg = 0.5
shock = 2.0
force_n = mass_kg * g * shock

# Two cap risers share load. Ignore the large triangular gusset and screen each
# as an 8 x 8 mm rectangular beam over the full 42 mm moment arm.
riser_count = 2
riser_b = 8.0
riser_h = 8.0
moment_arm_mm = 42.0
section_mm3 = riser_b * riser_h**2 / 6
stress_mpa = (force_n / riser_count * moment_arm_mm) / section_mm3
allowable_mpa = 8.0
safety = allowable_mpa / stress_mpa

# Dovetail bearing/shear, conservatively using only two 8 x 3 mm sections.
joint_area_mm2 = 2 * 8 * 3
joint_shear_mpa = force_n / joint_area_mm2
joint_allowable_mpa = 12.0
joint_safety = joint_allowable_mpa / joint_shear_mpa

# Cap roof bearing on two 14 x 2.4 mm shelves.
roof_area_mm2 = 2 * 14 * 2.4
roof_bearing_mpa = force_n / roof_area_mm2
roof_allowable_mpa = 20.0
roof_safety = roof_allowable_mpa / roof_bearing_mpa

lines = [
    f"Design load: {force_n:.2f} N (0.5 kg at 2g)",
    f"Cap-riser root stress: {stress_mpa:.2f} MPa",
    f"Cap-riser safety factor vs 8 MPa interlayer allowable: {safety:.2f}",
    f"Dovetail shear stress: {joint_shear_mpa:.3f} MPa",
    f"Dovetail shear safety factor: {joint_safety:.1f}",
    f"Cap-roof bearing stress: {roof_bearing_mpa:.3f} MPa",
    f"Cap-roof bearing safety factor: {roof_safety:.1f}",
]
print("\n".join(lines))

if min(safety, joint_safety, roof_safety) < 3:
    raise SystemExit("Screening safety factor below 3.0")
