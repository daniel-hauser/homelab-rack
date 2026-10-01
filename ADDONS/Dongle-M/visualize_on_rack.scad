// Non-production visualization only. The printable source is standalone.
// SPDX-License-Identifier: MIT

use <../../homelab_rack.scad>

part = "none";
include <dongle_m_holder.scad>

desk_preview();

translate([11, 150, 177.05])
    addon_assembly(true, 0);
