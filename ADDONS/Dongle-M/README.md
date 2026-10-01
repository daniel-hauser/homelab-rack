# SONOFF Dongle Max desktop-rack holder

**Prototype:** this add-on is designed from SONOFF's official **169 × 32.5 ×
22 mm** outer envelope. Connector, SMA, button, LED, vent and OEM-bracket
coordinates are unpublished, so verify a real device before unattended use.

It is a removable rear-spine bridge for the existing 4U desktop rack. No rack
part, production plate or OEM SONOFF bracket is modified. The two caps lower
onto the top 12 mm of the 14 × 5 mm rear spines; roofs carry vertical load,
close-fitting sleeves resist rotation, and captured dovetails lock the cradle
laterally. A removable snap strap prevents bounce-out.

## Published rack interface copied locally

`dongle_m_holder.scad` is standalone and duplicates only these released
interface values: 14 × 5 mm spine envelope; X = 11 and 216.3 mm; Y = 150 mm;
4U height = 177.05 mm. It does not include the root rack SCAD.

## Default dimensions

| Item | Default |
|---|---:|
| Dongle-M envelope | 169 × 32.5 × 22 mm |
| Device XY / Z clearance | 0.60 / 0.60 mm total |
| Spine fit clearance | 0.45 mm total |
| Clear span between spines | 191.30 mm |
| Spine rear to device front | 24 mm |
| Spine top to device bottom | 42 mm |
| Cap engagement | 12 mm |
| Cradle rails above device floor | 5 mm |

The device is centered between the spines. Its bottom is about 222 mm above
the desk and its front edge is 24 mm behind the spine rear face, leaving the
two 169 mm ends substantially open. Corner stops are only 3 mm long.

## Fit first

Print `STL\05_spine_fit_coupon.stl` first. Slide it down over the top of each
spine without forcing it. It should bottom on its roof, have no visible
rocking, leave the spine front/magnet area open, and pull off by hand with
steady upward force. If tight, increase `spine_xy_clearance` by 0.15 mm; if
loose, reduce it by 0.10 mm and re-export. Check that no cap surface touches
the UK-Ultra top or any rack module.

Before trusting the prototype, also check the real Dongle-M body dimensions,
connector cable bend, antenna sweep, LED/button visibility, ventilation, and
strap pressure. Do not use if the SMA locations conflict with the short corner
stops or strap.

## Print

- Bambu Lab A1, 0.4 mm nozzle, 0.20 mm Standard, Generic PLA or PETG.
- Four walls, five top, four bottom, 20% gyroid.
- Supports, brim and skirt off. Use the supplied STL orientations.
- Print the strap in PETG when frequent removal is expected; PLA is suitable
  for limited prototype cycles.
- `Bambu\Dongle-M-fit-first.3mf` contains only the coupon.
- `Bambu\Dongle-M-production.3mf` contains both caps, cradle and strap.

## Assembly

1. Validate both spines with the fit coupon.
2. Slide each cap onto the matching cradle dovetail from its outer end until
   the shallow roof detent clicks. The tall cap risers face the rack; rails
   face upward.
3. Lower the joined bridge straight down over both spine tops until both cap
   roofs seat. Do not twist one cap independently.
4. Place the Dongle-M in the low rails, route cables and articulate antennas.
5. Flex the strap legs outward, lower it at cradle center, and press both
   catches into the rail windows. To remove the device, release one catch and
   lift off the strap; the rack remains assembled.

The holder is intended for normal desktop orientation, not inverted transport.

## Files

- `dongle_m_holder.scad` — parameterized source and visualization.
- `STL\` — four production parts plus the fit coupon.
- `Bambu\` — isolated fit-first and production projects.
- `renders\assembled-on-rack.png` — non-production rack context.
- `renders\assembled-perspective.png` — labeled full-stack perspective.
- `renders\rear-side-access.png` — labeled rear/side access perspective.
- `renders\exploded-addon.png` — add-on-only exploded view.
- `validation.json` — mesh, bed-volume and native-slicer results.
- `load_check.txt` — conservative 0.5 kg at 2g screening.

Printed BOM: one left cap, one right cap, one cradle, one retaining strap.
