// Non-production visualization only. The printable source is standalone.
// SPDX-License-Identifier: MIT

use <../../homelab_rack.scad>

part = "none";
include <dongle_m_holder.scad>

desk_preview();

translate([11, 150, 177.05])
    addon_assembly(true, 0);

// Render-only labels distinguish the two devices in perspective views.
color([0.18, 0.19, 0.21])
    translate([115.15, 73, 218.1])
        linear_extrude(0.35)
            text("UK-ULTRA / SWISS ARMY KNIFE",
                 size = 7, halign = "center", valign = "center");

color([0.94, 0.95, 0.96])
    translate([120.65, 195.55, 241.2])
        linear_extrude(0.35)
            text("SONOFF DONGLE-M",
                 size = 5.5, halign = "center", valign = "center");
