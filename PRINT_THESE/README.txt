HOMELAB RACK - PRINT-ONLY PACKAGE
=================================

The "STLs" folder contains exactly the 10 parts needed for the current
desktop rack. It contains no blanks, alternate variants, or fit-test coupons.

ALREADY PRINTED THE OLDER TEST PLATE
====================================

Double-click OPEN_NO_TEST_PROJECT.cmd or open
homelab-rack-Bambu-Studio-5-plates-NO-TEST.3mf.

Use this five-plate project for the fewest printer visits. It excludes every
fit coupon, seam coupon, rack-ear coupon, polarity key, and old test-only part.
It contains every final assembly object exactly once. The primary NO-TEST
project is the recommended targeted-support variant. Use
homelab-rack-Bambu-Studio-5-plates-NO-TEST-NO-SUPPORT.3mf only if you
deliberately want the native A/B baseline.

The revised 04_Desktop_Feet_Set.stl is intentionally included. The foot stack
peg and magnet geometry changed, so feet from the older test plate are
obsolete. No other test-only artifact is needed: the final rail-guided vent
and both rear spines are already included.

WAVESHARE POE M.2 HAT+ (B) REPLACEMENT

If the dual-Pi chassis has not been printed, use:

  REPLACEMENTS\PI-HAT-5MM-CLEARANCE\

Print its standalone 3MF instead of the old chassis object on Plate 3. Do not
reprint either Pi drawer or the vent. The replacement changes only the outer
Pi insertion openings from 30 mm to 35 mm.

PI DRAWER 6 MM MAGNET-POCKET REPLACEMENT

If nominal 6 mm magnets do not enter the printed drawer pockets, use:

  REPLACEMENTS\PI-MAGNET-POCKET-6MM\

This package replaces both drawers only. The chassis and vent remain unchanged.
Use glue; do not press-fit magnets and do not drill through the insulating roof.

PI COMPLETE SINGLE-PLATE PROJECT

If the corrected chassis and both corrected drawers are still unprinted, use:

  REPLACEMENTS\PI-COMPLETE-SINGLE-PLATE\

This single A1 plate contains those three objects only. It excludes the vent
and preserves targeted support only beneath the chassis's raised front rails.

Plate 1: UCG-Ultra module + rear spine A
Plate 2: left USW-Ultra module + rear spine B
Plate 3: dual-Pi chassis + final rail-guided vent cartridge
Plate 4: right USW-Ultra module + Pi drawer 2
Plate 5: UK-Ultra top + Pi drawer 1 + revised desktop feet set

Targeted-support estimate: 517.58 g PLA and 23h13m19s serial printing time,
0.88 g and 6m23s above the no-support baseline. The maximum classified bridge
is 18.84 mm.

Native A/B analysis found no UCG/USW roof over the device cavity. The concerning
17.51-17.52 mm paths are the forward seam-side corner-post top caps. One small
7 x 7 mm manual support column is generated under that cap on the UCG. It
starts on the internal bottom cap because build-plate-only support
cannot enter the enclosed corner-post cavity. Pull it out through the open
front/seam-side corner after printing.

The equivalent seam-side location on each USW overlaps the 34 mm-deep keystone
clearance, and the opposite side is the rack-ear/slot region. Both USWs remain
unsupported rather than violating those protected interfaces for a validated
17.52 mm bridge.

There is no support around magnet pockets, pegs/sockets, seam keys/towers,
rack-ear slots, device rails, keystone openings, rear-spine interfaces, or
rear corner cavities. Only plate 1 receives support.
Bambu clears floating-region banners globally in manual-support mode; the
tracked audit verifies actual support extrusion rather than relying on banners.

Five plates are the geometric minimum. Each of the four chassis and the
UK-Ultra top is over 241 mm wide and at least 150 mm deep in its validated
axis-aligned print orientation, so no two can share a 256 x 256 mm A1 bed.

HAVE NOT PRINTED A TEST PLATE
==============================

Fastest way to load the original test-first workflow:

1. Extract the ZIP.
2. Double-click OPEN_IN_BAMBU_STUDIO.cmd.
3. Bambu Studio opens homelab-rack-Bambu-Studio-6-plates.3mf with a useful
   validation plate first, followed by five production plates.
4. Confirm your installed A1 0.4 mm printer and actual filament before
   printing. The included project is already sliced natively by Bambu Studio.

Both projects were prepared with an A1 0.4 mm nozzle, 0.20 mm layers, 4 walls,
5 top layers, 4 bottom layers, 20% gyroid, no supports, no brim, and no skirt.

Loose magnets physically attract all four intended assembled Pi/HAT screw
heads, so screw ferromagnetism is accepted. Do not print another test coupon
for the Pi mount. Print only STLs\05_Pi_Drawer_1.stl first with the pinned
profile, install four magnets, seat the actual Pi/HAT assembly, and verify
retention, locator engagement, drawer insertion, and the installed holder gap.
Print Drawer 2 only after this first article passes.

After Drawer 1 passes, print the tracked project in this order: plate 2 UCG,
plate 3 left USW, plate 4 dual-Pi chassis, plate 5 right USW plus Drawer 2,
then plate 6 UK-Ultra top with its already-printed Drawer 1 object disabled.
Plate 1 is the existing test-first plate and does not need to be reprinted.

Candidate total: 547.11 g PLA and 24h43m51s across six plates. Plate 1 is
67.80 g / 3h29m28s and includes both rear spines, the vent, all four feet,
the polarity key, and the required fit coupons.

Exposed chassis and UK-Ultra cap corners use restrained 1.5 mm support-free
chamfers. The removable Pi and vent faceplates use 1.2 mm chamfers. Functional
seam, rack, bay, and rear-spine dimensions are unchanged. The two front
stacking pairs were relocated rearward to clear the full-depth rack slots.

This revision uses reinforced 8 x 14 mm seam towers with 45-degree floor
buttresses. The reinforcement adds 17.75 g across the complete rack.
Physical coupon testing confirmed clean seam-tower prints and easy engagement.
The paired modules have a 0.0 mm designed face gap and 1.5 mm of axial socket
reserve so the tower faces can close without the keys bottoming out.

The two rear-spine STL files are intentionally identical: print one of each.

The rack-ear profile visually matches existing rack hardware and retains the
validated 482.60 mm outer width and 465.10 mm mounting centers.

The Pi drawers use four 6 x 2 mm magnet pockets beneath the existing lower
screw heads, with printed side/corner locators carrying shear. Loose-magnet
attraction has passed on all four assembled screw heads. The current CAD
assumes 1.60 mm protrusion, a 0.35 mm working gap, and a 0.30 mm insulating
skin; the exact installed gap remains a Drawer 1 first-article check. The
through-floor alternative remains review-only.

The vent is now a lightweight full-depth cartridge rather than a shallow
friction plate. Its proven 64.5 x 30 mm face is unchanged. Two 111 mm
L-section runners engage the same chassis tracks as the Pi drawers for 77 mm,
with 0.15 mm side clearance and 2.0 mm reserve before the rear stop. A light
rear chevron prevents racking without blocking airflow. Print the cartridge
face-down as exported; both chevron legs grow inward from supported runners.

The vent and Pi cartridges click into paired service detents behind the front
face. Their 0.65 mm pockets provide 0.20 mm relief beyond the 0.45 mm local
engagement, so the detents retain without overconstraining the guide tracks.
Push straight in until both sides click. Remove by gripping the projecting
faceplate edges and pulling evenly; rear ramps cam the spring arms inward. The
validated 62 x 30 mm opening is unchanged, and its 1.2 mm receiving chamfer
seats the faceplate flush.

Every vertical module/cap joint has four magnet pairs and four independent
peg/socket pairs. The front pairs are relocated behind the rack-slot cut depth;
handed rack ears therefore cannot open a pocket or create a magnet-to-empty
pair. Four additional pairs clamp the removable feet to the bottom module.

The two rear spines add two horizontal magnet/peg pairs per module. They align
and brace the rear of the four-module desktop stack against racking, but they
do not replace the four vertical corner clamps at each stack joint.

All pockets use the same 6 x 2 mm discs. A fully populated desktop build uses
64 magnets: 40 in 20 vertical stack/foot pairs, 16 in 8 rear-spine pairs, and
8 beneath the Pi screw heads. Side-seam magnets are only needed later when
pairing halves in a 19-inch rack.

Polarity is globally consistent: marked face up (+Z) for stack/foot magnets,
toward the rear (+Y) for module/spine pairs, and toward rack right (+X) for
future side-seam pairs. Pi polarity is not functional against steel, but
marked-face-up installation is preferred for consistency.

The six-plate project was validated and sliced natively with Bambu Studio
02.08.02.61. Its skeleton and skin line widths are explicit millimetre values,
which avoids the "Line width too large" / "100.000000" import error.

Bambu Studio may warn that the four full-height chassis have a "floating
cantilever." Its conservative overhang detector sees the short 45-degree seam
keys, socket roofs, and hollow tower caps. The UCG, both USW modules, and
dual-Pi chassis have no slicer-classified bridge longer than 17.52 mm.
Automatic supports fill large empty areas to reach those small surfaces, add
substantial print time, and obstruct the pockets. Print plate 1 first, then
keep supports disabled for the full-height production chassis if its
seam-tower coupons print cleanly.

The redesigned Pi drawers, vent insert, and UK-Ultra top slice without
warnings. Their independently measured maximum bridge spans are 6.39 mm,
12.40 mm, and 16.74 mm respectively.

Plate 1 is explicitly axis-aligned rather than automatically rotated. Its
maximum bridge is 18.84 mm, with 12.58 mm on the fit coupon, no bridge paths on
the polarity key, and 12.23 mm on each rear spine.

Plate 5 keeps the right USW module at exact 0-degree XY rotation. The print
face is unchanged, but this avoids a slicer-only diagonal bridge path that
appeared with a near-180-degree transform; the validated maximum is 17.52 mm.

All 20 packaged STLs were also sliced independently with native Bambu Studio:
20 pass, no unexpected warnings, and no bridge over 18.84 mm. The unchanged
chassis warning is matched by exact male/female seam-tower coupons generated
from the same OpenSCAD modules; those coupons slice without warnings at
4.66 mm and 7.10 mm maximum bridge.
