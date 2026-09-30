PI MOUNT ALTERNATIVES - REVIEW ONLY
===================================

These files document the selected magnetic Raspberry Pi 5 mounting direction
and its through-floor fallback. The magnetic direction remains physically
gated and is not final until all four screw heads pass the attraction test and
the installed screw-head height is measured.

A_Magnetic_Cradle_Review.stl - selected direction, physically gated
  Four 6 x 2 mm magnet glue pockets align to the accessible lower screw heads
  on the official 58 x 49 mm Pi pattern. A provisional 0.30 mm printed
  insulating skin separates each magnet from the screw-head recess. Four side
  tabs and two rear-corner stops carry shear while leaving the central rear
  microSD area open.

  Preview-only assumptions:
  - installed screw-head protrusion below PCB: 1.60 mm;
  - target screw-head-to-skin gap: 0.35 mm;
  - printed insulating skin: 0.30 mm;
  - magnet pocket diameter: 6.25 mm;
  - magnet position: Z 2.55 to 4.55 mm above the drawer underside.

  Install each magnet from the drawer underside, hold it against the printed
  roof while epoxy cures, and optionally fill the remaining access recess
  flush. Polarity does not affect attraction to steel; install all four with
  the same pole facing the PCB for consistency. Do not use this option until
  all four screw heads show strong attraction to a loose 6 x 2 mm magnet.

B_Through_Floor_M2.5_Review.stl - review fallback only
  Four M2.5 clearance holes and recessed head counterbores align to the same
  58 x 49 mm pattern. The replacement screw passes through the 1.20 mm local
  printed shoulder, the Pi PCB, and into the existing female HAT standoff.
  The screw head remains recessed above the drawer underside.

  Required replacement length:
    measured existing under-head screw length + exactly 1.20 mm

  No purchased screw length is specified until the existing screw length,
  head geometry, and usable female-standoff thread depth are measured.

Required user measurements and checks
-------------------------------------
1. Confirm a loose 6 x 2 mm magnet strongly attracts each of the four exposed
   lower screw heads individually.
2. Measure each screw head's protrusion below the PCB; report the minimum and
   maximum, in mm.
3. Measure screw-head diameter and height, in mm.
4. Measure the existing underside screw length under the head, thread
   diameter/pitch, and the usable female-standoff thread depth.
5. Confirm the actual magnets' diameter and thickness and, if known, grade.
6. Weigh the complete Pi + cooler + HAT + NVMe assembly if a scale is
   available; otherwise the retention calculation will retain a conservative
   0.20 kg design mass.

The OpenSCAD source keeps both concepts parameterized through the shared
pi_cartridge() and pi_cartridge_retention_cuts() modules.
