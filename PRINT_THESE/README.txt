HOMELAB RACK - PRINT-ONLY PACKAGE
=================================

The "STLs" folder contains exactly the 10 parts needed for the current
desktop rack. It contains no blanks, alternate variants, or fit-test coupons.

Fastest way to load everything:

1. Extract the ZIP.
2. Double-click OPEN_IN_BAMBU_STUDIO.cmd.
3. Bambu Studio opens homelab-rack-Bambu-Studio-6-plates.3mf with a useful
   validation plate first, followed by five production plates.
4. Confirm your installed A1 0.4 mm printer and actual filament before
   printing. The included project is already sliced natively by Bambu Studio.

The project was prepared with an A1 0.4 mm nozzle, 0.20 mm layers, 4 walls,
5 top layers, 4 bottom layers, 20% gyroid, no supports, no brim, and no skirt.

Expected total: 528.99 g PLA and 23h04m41s across six plates. Plate 1 is
63.30 g / 2h45m11s and includes both rear spines, the vent, all four feet,
the polarity key, and the required fit coupons.

Exposed chassis and UK-Ultra cap corners use restrained 1.5 mm support-free
chamfers. The removable Pi and vent faceplates use 1.2 mm chamfers. Functional
stacking, seam, rack, bay, magnet, and rear-spine interfaces are unchanged.

This revision uses reinforced 8 x 14 mm seam towers with 45-degree floor
buttresses. The reinforcement adds 17.75 g across the complete rack.
Physical coupon testing confirmed clean seam-tower prints and easy engagement.
The paired modules have a 0.0 mm designed face gap and 1.5 mm of axial socket
reserve so the tower faces can close without the keys bottoming out.

The two rear-spine STL files are intentionally identical: print one of each.

The rack-ear profile visually matches existing rack hardware and retains the
validated 482.60 mm outer width and 465.10 mm mounting centers.

All magnet pockets now use the same 6 x 2 mm disc magnets. A fully populated,
reorderable desktop build uses 52 magnets: 36 for module/cap stacking and
16 for the two rear spines and their module-side mating pockets. Side-seam
magnets are only needed later when pairing halves in a 19-inch rack.

The six-plate project was validated and sliced natively with Bambu Studio
02.08.02.61. Its skeleton and skin line widths are explicit millimetre values,
which avoids the "Line width too large" / "100.000000" import error.

Bambu Studio may warn that the four full-height chassis have a "floating
cantilever." Its conservative overhang detector sees the short 45-degree seam
keys, socket roofs, and hollow tower caps. The UCG, both USW modules, and
dual-Pi chassis have no slicer-classified bridge longer than 13.79 mm.
Automatic supports fill large empty areas to reach those small surfaces, add
substantial print time, and obstruct the pockets. Print plate 1 first, then
keep supports disabled for the full-height production chassis if its
seam-tower coupons print cleanly.

The redesigned Pi drawers, vent insert, and UK-Ultra top slice without
warnings. Their independently measured maximum bridge spans are 6.37 mm,
12.89 mm, and 16.76 mm respectively.

Plate 1 is explicitly axis-aligned rather than automatically rotated. Its
maximum bridge is 18.70 mm, with 9.23 mm on the fit coupon, no bridge paths on
the polarity key, and 10.68 mm on each rear spine.

All 20 packaged STLs were also sliced independently with native Bambu Studio:
20 pass, no unexpected warnings, and no bridge over 18.70 mm. The unchanged
chassis warning is matched by exact male/female seam-tower coupons generated
from the same OpenSCAD modules; those coupons slice without warnings at
4.66 mm and 7.10 mm maximum bridge.
