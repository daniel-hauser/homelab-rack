// SONOFF Dongle Max (Dongle-M) desktop-rack add-on
// Prototype based on the official 169 x 32.5 x 22 mm outer envelope.
// SPDX-License-Identifier: MIT

$fn = 48;

part = is_undef(part) ? "assembly" : part; // printable names, exploded, assembly, none

// Published rack interface constants duplicated from homelab_rack.scad.
spine_w = 14;
spine_d = 5;
spine_left_x = 11;
spine_right_x = 216.3;
spine_y = 150;
spine_h = 177.05;

// Device and fit parameters.
device = [169, 32.5, 22];
xy_clearance = 0.60; // total added clearance per device axis
z_clearance = 0.60;
spine_xy_clearance = 0.45; // total diametral/width clearance
rear_offset = 24; // spine rear face to device envelope
cradle_height = 42; // spine top to device bottom

wall = 2.4;
rail_h = 5;
base_t = 3;
strap_w = 8;
cap_engagement = 12;
cap_roof = 2.4;
joint_len = 8;
joint_h = 6;
joint_bottom_w = 8;
joint_top_w = 12;
chamfer = 1.2;

inner_span = spine_right_x - (spine_left_x + spine_w); // 191.3 mm
device_w = device[0] + xy_clearance;
device_d = device[1] + xy_clearance;
device_h = device[2] + z_clearance;
device_x = (inner_span - device_w) / 2;
tray_y = rear_offset;
joint_y = tray_y + device_d / 2;
tray_outer_d = device_d + 2 * wall;
joint_z = cradle_height - base_t;

module chamfered_box(size, c = chamfer) {
    hull() {
        for (x = [c, size[0] - c])
            for (y = [c, size[1] - c])
                translate([x, y, 0])
                    cylinder(r = c, h = size[2]);
    }
}

module dovetail_key(length = joint_len, clearance = 0) {
    linear_extrude(height = length)
        polygon([
            [-joint_bottom_w / 2 + clearance, 0],
            [ joint_bottom_w / 2 - clearance, 0],
            [ joint_top_w / 2 - clearance, joint_h],
            [-joint_top_w / 2 + clearance, joint_h]
        ]);
}

module cradle() {
    difference() {
        union() {
            // Three crossbars and two low rails leave both device ends open.
            for (x = [device_x + 18, inner_span / 2, device_x + device_w - 18])
                translate([x - 4, tray_y - wall, 0])
                    chamfered_box([8, tray_outer_d, base_t], 0.8);

            for (y = [tray_y - wall, tray_y + device_d])
                translate([device_x - 3, y, 0])
                    chamfered_box([device_w + 6, wall, base_t + rail_h], 0.9);

            // Short corner stops prevent lateral walking but preserve connectors.
            for (x = [device_x - 3, device_x + device_w])
                for (y = [tray_y - wall, tray_y + device_d])
                    translate([x, y, 0])
                        chamfered_box([3, wall, base_t + rail_h], 0.7);

            // Stiff, triangulated end arms carry the tray into the spine-cap joints.
            for (side = [0, 1]) {
                x0 = side == 0 ? 0 : inner_span - joint_len;
                translate([x0, joint_y - joint_bottom_w / 2, 0])
                    rotate([90, 0, 90])
                        dovetail_key(joint_len);

                // A shallow printed bump clicks into the cap-roof recess.
                translate([side == 0 ? joint_len - 1.5 : inner_span - joint_len,
                           joint_y - 1.2, joint_h])
                    chamfered_box([1.5, 2.4, 0.35], 0.3);

                hull() {
                    translate([side == 0 ? joint_len : inner_span - joint_len - 6,
                               joint_y - 5, 0])
                        cube([6, 10, base_t]);
                    translate([side == 0 ? device_x + 14 : device_x + device_w - 22,
                               joint_y - 5, 0])
                        cube([8, 10, base_t]);
                }
            }
        }

        // Snap-strap catch windows in the two rails.
        for (y = [tray_y - wall - 0.1, tray_y + device_d - 0.1])
            translate([inner_span / 2 - strap_w / 2, y, base_t + 1.1])
                cube([strap_w, wall + 0.2, 2.2]);
    }
}

module cap_sleeve() {
    inner_w = spine_w + spine_xy_clearance;
    inner_d = spine_d + spine_xy_clearance;
    outer_w = inner_w + 2 * wall;
    outer_d = inner_d + 2 * wall;

    difference() {
        union() {
            translate([-wall - spine_xy_clearance / 2,
                       -wall - spine_xy_clearance / 2,
                       -cap_engagement])
                chamfered_box([outer_w, outer_d, cap_engagement + cap_roof], 0.9);
            translate([-wall - spine_xy_clearance / 2,
                       -wall - spine_xy_clearance / 2,
                       0])
                chamfered_box([outer_w, outer_d, cap_roof], 0.9);
        }
        translate([-spine_xy_clearance / 2,
                   -spine_xy_clearance / 2,
                   -cap_engagement - 0.1])
            cube([inner_w, inner_d, cap_engagement + 0.2]);

        // Keep the spine front, its top magnet and its peg interface unobstructed.
        translate([wall + 0.8, -wall - 0.4, -cap_engagement - 0.2])
            cube([spine_w - 2 * (wall + 0.8), wall + 1.0, cap_engagement + 0.4]);
    }
}

module cap(left = true) {
    socket_x = left ? spine_w + wall : -joint_len - wall;
    socket_open_x = left ? socket_x - 0.1 : socket_x - 0.1;
    riser_x = left ? spine_w - 8 : 0;
    beam_x = left ? spine_w - 8 : 0;
    socket_center_y = spine_d + rear_offset + device_d / 2;

    difference() {
        union() {
            cap_sleeve();

            // Riser and 45-degree rear gusset.
            translate([riser_x, spine_d - 2.4, 0])
                chamfered_box([8, 8, cradle_height + joint_h], 0.8);
            hull() {
                translate([beam_x, spine_d, cradle_height - 3])
                    cube([8, 5, 3]);
                translate([beam_x, socket_center_y - 7, cradle_height - 3])
                    cube([8, 7, 3]);
                translate([beam_x, spine_d, 4])
                    cube([8, 5, 3]);
            }

            // Dovetail socket block; the cradle slides in from the rack center.
            translate([left ? spine_w - 0.1 : -joint_len + 0.1,
                       socket_center_y - joint_top_w / 2 - wall,
                       cradle_height - base_t - wall])
                chamfered_box([joint_len + 0.2,
                               joint_top_w + 2 * wall,
                               joint_h + 2 * wall], 0.8);
        }

        translate([left ? spine_w - 0.2 : -joint_len + 0.2,
                   socket_center_y,
                   cradle_height - base_t])
            rotate([90, 0, 90])
                dovetail_key(joint_len + 0.4, -0.28);

        // Roof recess captures the matching 0.35 mm key bump.
        translate([left ? spine_w + joint_len - 1.5 : -joint_len - 0.1,
                   socket_center_y - 1.4,
                   cradle_height - base_t + joint_h - 0.1])
            cube([1.8, 2.8, 0.65]);
    }
}

module retaining_strap() {
    inner_d = tray_outer_d + 0.50;
    inner_h = device_h + base_t + 0.45;
    leg_t = 2.0;
    top_t = 2.0;

    union() {
        translate([-strap_w / 2, -wall - leg_t, 0])
            chamfered_box([strap_w, leg_t, inner_h + top_t], 0.7);
        translate([-strap_w / 2, tray_outer_d - wall, 0])
            chamfered_box([strap_w, leg_t, inner_h + top_t], 0.7);
        translate([-strap_w / 2, -wall - leg_t, inner_h])
            chamfered_box([strap_w, inner_d + 2 * leg_t, top_t], 0.7);

        // Inward catches engage the cradle windows.
        translate([-strap_w / 2, -wall, 1.25])
            cube([strap_w, 1.0, 1.8]);
        translate([-strap_w / 2, tray_outer_d - wall - 1.0, 1.25])
            cube([strap_w, 1.0, 1.8]);
    }
}

module fit_coupon() {
    difference() {
        union() {
            cap_sleeve();
            translate([-wall - spine_xy_clearance / 2, spine_d + wall, -cap_engagement])
                chamfered_box([spine_w + 2 * wall + spine_xy_clearance, 12, 3], 0.8);
        }
        translate([spine_w / 2 - 1, spine_d + wall + 4, -cap_engagement - 0.1])
            cube([2, 4, 3.2]);
    }
}

module dummy_dongle() {
    color([0.72, 0.74, 0.76])
        translate([device_x + xy_clearance / 2, tray_y + xy_clearance / 2, base_t])
            chamfered_box(device, 2.0);

    // Non-authoritative antennas: visualization only.
    for (x = [device_x + 22, device_x + device_w - 22]) {
        color([0.82, 0.68, 0.18])
            translate([x, tray_y + device_d + 2.5, base_t + 11])
                rotate([90, 0, 0])
                    cylinder(d = 6, h = 5);
        color([0.10, 0.10, 0.11])
            translate([x, tray_y + device_d + 5, base_t + 11])
                rotate([-35, 0, 0])
                    cylinder(d = 8, h = 72);
    }
}

module addon_assembly(show_device = true, explode = 0) {
    translate([0, 0, explode])
        color([0.12, 0.14, 0.18])
            cap(true);
    translate([spine_right_x - spine_left_x, 0, explode])
        color([0.12, 0.14, 0.18])
            cap(false);
    translate([spine_w, spine_d, cradle_height - base_t + 2 * explode])
        color([0.19, 0.22, 0.27])
            cradle();
    translate([spine_w + inner_span / 2,
               spine_d + tray_y,
               cradle_height - base_t + 3 * explode])
        color([0.28, 0.31, 0.36])
            retaining_strap();
    if (show_device)
        translate([spine_w, spine_d, cradle_height - base_t + 2 * explode])
            dummy_dongle();
}

module rack_context() {
    // Visualization-only copy of the published 4U envelope and rear spines.
    color([0.15, 0.17, 0.20, 0.8])
        cube([230.3, 150, 180]);
    color([0.08, 0.09, 0.11]) {
        translate([spine_left_x, spine_y, 0])
            cube([spine_w, spine_d, spine_h]);
        translate([spine_right_x, spine_y, 0])
            cube([spine_w, spine_d, spine_h]);
    }
    color([0.10, 0.12, 0.16])
        translate([0, 0, 180])
            cube([230.3, 150, 4]);
    color([0.86, 0.87, 0.89])
        translate([(230.3 - 137) / 2, 31, 184])
            chamfered_box([137, 84, 34], 2);
}

module left_cap_print() {
    translate([0, 0, cap_engagement])
        cap(true);
}

module right_cap_print() {
    translate([0, 0, cap_engagement])
        cap(false);
}

module strap_print() {
    translate([0, 0, strap_w / 2])
        rotate([0, 90, 0])
            retaining_strap();
}

if (part == "left_cap")
    left_cap_print();
else if (part == "right_cap")
    right_cap_print();
else if (part == "cradle")
    cradle();
else if (part == "strap")
    strap_print();
else if (part == "fit_coupon")
    translate([0, 0, wall + spine_xy_clearance / 2])
        rotate([90, 0, 0])
            fit_coupon();
else if (part == "exploded")
    addon_assembly(true, 12);
else if (part == "assembly") {
    rack_context();
    translate([spine_left_x, spine_y, spine_h])
        addon_assembly(true, 0);
}
