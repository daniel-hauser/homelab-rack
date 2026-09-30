/*
  SPDX-License-Identifier: CERN-OHL-S-2.0

  Modular half-width homelab rack for a Bambu Lab A1.

  Coordinate system:
    X = module width, Y = depth (front at 0), Z = height.

  Export examples:
    openscad -o out/ucg_left.stl -D 'part="ucg_left"' homelab_rack.scad
    openscad -o out/desk_preview.png --render -D 'part="desk_preview"' homelab_rack.scad
*/

$fn = 48;

part = "desk_preview";

// Printer/material tuning
fit_clearance = 0.35;
peg_clearance = 0.30;
magnet_clearance = 0.25;
keystone_clearance = 0.30;

// EIA-310 / IEC 60297
rack_width = 482.60;
half_width = rack_width / 2;
rack_hole_centers = 465.10;
rack_hole_edge = (rack_width - rack_hole_centers) / 2;
u_height = 44.45;
panel_height = 43.70;
rack_hole_z = [6.35, 22.225, 38.10];
rack_ear_width = 17.5;
rack_ear_relief = 2.0;
rack_ear_forward = 2.0;
rack_ear_thickness = 5.0;

// Shared module geometry
module_depth = 150;
base_thickness = 1.8;
front_thickness = 3.0;
rear_thickness = 3.0;
corner_size = 16;
exterior_chamfer = 1.5;
faceplate_chamfer = 1.2;

// User-available magnets
stack_magnet_d = 6;
stack_magnet_h = 2;
side_magnet_d = 6;
side_magnet_h = 2;
side_key_root = 7.2;
side_key_tip = 5.6;
side_key_length = 3.2;
side_key_socket_extra = 1.7;
side_join_y = [46, module_depth - 16];
side_join_tower_w = 8;
side_join_tower_d = 14;
side_join_gusset_run = 10;

// Verified equipment envelopes
ucg_size = [141.8, 127.6, 30.0];
usw_size = [203.0, 76.0, 33.0];
pi_board = [56.0, 85.0, 1.6]; // Rotated: connector edge faces front
poe_hat_plan = [56.0, 85.0];  // Waveshare PoE M.2 HAT+ (B)
pi_side_margin = 20.0;
pi_mount_height = 6.8;
pi_mount_boss_d = 8.0;
pi_mount_screw_d = 2.8;
pi_mount_head_clearance_d = 5.6;
pi_mount_shoulder = 1.2;
pi_mount_pattern_x = [3.5, 52.5];
pi_mount_pattern_y = [3.5, 61.5];
pi_locator_clearance = 0.30;

// Magnetic production direction; dimensions remain physically gated.
pi_magnetic_assumed_screw_head_d = 5.0;
pi_magnetic_assumed_screw_head_h = 1.6;
pi_magnetic_target_gap = 0.35;
pi_magnetic_insulating_skin = 0.30;
pi_magnet_pocket_d = stack_magnet_d + magnet_clearance;
bay_count = 3;
bay_width = 62.0;
bay_gap = 4.0;
bay_start = (
    half_width - bay_count * bay_width - (bay_count - 1) * bay_gap
) / 2;
bay_opening_z = 6.0;
bay_opening_h = 30.0;
bay_depth = 112.0;
bay_clearance = 0.40;
cartridge_detent_z = 13.0;
cartridge_detent_h = 4.0;
cartridge_detent_arm_t = 1.0;
cartridge_detent_arm_y = 2.2;
cartridge_detent_arm_len = 15.8;
cartridge_detent_peak_y = 14.0;
cartridge_detent_protrusion = 0.45;
cartridge_detent_pocket_depth = 0.65;
vent_cartridge_depth = bay_depth - 1.0;
vent_runner_x = bay_clearance + 0.8;
vent_runner_w = 3.0;
vent_runner_floor_t = 1.8;
vent_runner_h = 3.4;
vent_chevron_w = 1.8;
vent_chevron_start_y = vent_cartridge_depth - 36.0;
vent_chevron_peak_y = vent_cartridge_depth - 3.0;
bay_fit_coupon_depth = 50.0;
uk_ultra_size = [137.0, 84.0, 34.0];
uk_ultra_clearance = 1.20;

keystone_cutout = [
    14.5 + keystone_clearance,
    16.0 + keystone_clearance
];
keystone_top_clearance = 1.0;
keystone_body = [16.5, 32.0, 18.0];
face_clearance_depth = 34.0;

module rack_slot(x, z, length = 10.0, diameter = 7.0) {
    hull() {
        for (dz = [-length / 2 + diameter / 2, length / 2 - diameter / 2])
            translate([x, corner_size + 0.2, z + dz])
                rotate([90, 0, 0])
                    cylinder(
                        d = diameter,
                        h = corner_size + rack_ear_forward + 0.4
                    );
    }
}

module face_cutout(x, z, width, height) {
    translate([x, -0.2, z])
        cube([width, face_clearance_depth + 0.4, height]);
}

module bay_face_cutout(x, z) {
    face_cutout(x, z, bay_width, bay_opening_h);

    hull() {
        translate([
            x - faceplate_chamfer,
            -0.2,
            z - faceplate_chamfer
        ])
            cube([
                bay_width + 2 * faceplate_chamfer,
                0.01,
                bay_opening_h + 2 * faceplate_chamfer
            ]);
        translate([x, faceplate_chamfer, z])
            cube([bay_width, 0.01, bay_opening_h]);
    }
}

module bay_service_detent_pockets(x, z) {
    pocket_y = cartridge_detent_peak_y - 4.2;
    pocket_len = 8.4;

    translate([
        x - cartridge_detent_pocket_depth,
        pocket_y,
        z + cartridge_detent_z
    ])
        cube([
            cartridge_detent_pocket_depth + 0.1,
            pocket_len,
            cartridge_detent_h
        ]);
    translate([
        x + bay_width - 0.1,
        pocket_y,
        z + cartridge_detent_z
    ])
        cube([
            cartridge_detent_pocket_depth + 0.1,
            pocket_len,
            cartridge_detent_h
        ]);
}

module cartridge_service_detents() {
    left_x = bay_clearance;
    right_x = bay_width - bay_clearance;
    detent_end_y = cartridge_detent_arm_y
        + cartridge_detent_arm_len;
    slope_end_y = cartridge_detent_peak_y - 0.6;
    root_z = base_thickness;

    for (x = [
        left_x,
        right_x - cartridge_detent_arm_t
    ]) {
        hull() {
            translate([
                x,
                cartridge_detent_arm_y,
                root_z
            ])
                cube([
                    cartridge_detent_arm_t,
                    0.8,
                    cartridge_detent_h
                ]);
            translate([
                x,
                slope_end_y,
                cartridge_detent_z
            ])
                cube([
                    cartridge_detent_arm_t,
                    0.8,
                    cartridge_detent_h
                ]);
        }
        translate([
            x,
            slope_end_y,
            cartridge_detent_z
        ])
            cube([
                cartridge_detent_arm_t,
                detent_end_y - slope_end_y,
                cartridge_detent_h
            ]);
    }

    translate([0, 0, cartridge_detent_z])
        linear_extrude(height = cartridge_detent_h) {
            polygon([
                [left_x + 0.2, cartridge_detent_peak_y - 4],
                [left_x + 0.2, detent_end_y],
                [
                    -cartridge_detent_protrusion,
                    cartridge_detent_peak_y
                ]
            ]);
            polygon([
                [right_x - 0.2, cartridge_detent_peak_y - 4],
                [
                    bay_width + cartridge_detent_protrusion,
                    cartridge_detent_peak_y
                ],
                [right_x - 0.2, detent_end_y]
            ]);
        }
}

module bay_guide_lips(
    x,
    z,
    start_y = face_clearance_depth,
    length = bay_depth - face_clearance_depth + front_thickness
) {
    guide_w = 0.65;

    for (guide_x = [
        x + bay_clearance,
        x + bay_width - bay_clearance - guide_w
    ])
        translate([guide_x, start_y, z])
            cube([guide_w, length, 2.4]);
}

module keystone_cutout_at(x, z = 13.7) {
    face_cutout(
        x,
        z,
        keystone_cutout[0],
        keystone_cutout[1] + keystone_top_clearance
    );
}

module xy_corner_chamfer_cut(chamfer, height) {
    linear_extrude(height = height)
        polygon([
            [-0.2, -0.2],
            [chamfer + 0.2, -0.2],
            [-0.2, chamfer + 0.2]
        ]);
}

module rectangular_corner_chamfer_cuts(
    width,
    depth,
    height,
    chamfer = exterior_chamfer
) {
    for (x_side = [0, 1])
        for (y_side = [0, 1])
            translate([
                x_side ? width : 0,
                y_side ? depth : 0,
                -0.2
            ])
                mirror([x_side, 0, 0])
                    mirror([0, y_side, 0])
                        xy_corner_chamfer_cut(
                            chamfer,
                            height + 0.4
                        );
}

module exposed_module_corner_chamfer_cuts(hand) {
    outer_x = hand == "left" ? 0 : half_width;

    for (front = [0, 1])
        translate([
            outer_x,
            front ? -rack_ear_forward : module_depth,
            -0.2
        ])
            mirror([hand == "right" ? 1 : 0, 0, 0])
                mirror([0, front ? 0 : 1, 0])
                    xy_corner_chamfer_cut(
                        exterior_chamfer,
                        panel_height + 3.6
                    );
}

module chamfered_front_flange(
    width,
    depth,
    height,
    chamfer = faceplate_chamfer
) {
    rotate([90, 0, 0])
        linear_extrude(height = depth)
            polygon([
                [chamfer, 0],
                [width - chamfer, 0],
                [width, chamfer],
                [width, height - chamfer],
                [width - chamfer, height],
                [chamfer, height],
                [0, height - chamfer],
                [0, chamfer]
            ]);
}

module honeycomb_plate(
    width,
    depth,
    thickness,
    edge = 7,
    cell_r = 11,
    hole_r = 8.9
) {
    x_pitch = 1.5 * cell_r;
    y_pitch = sqrt(3) * cell_r;

    // Flat-top hexagonal openings leave a continuous three-direction PLA web.
    // The solid perimeter carries side-wall, corner and rack-ear loads.
    difference() {
        cube([width, depth, thickness]);

        for (ix = [0 : ceil(width / x_pitch)])
            for (iy = [0 : ceil(depth / y_pitch)])
                let(
                    x = edge + hole_r + ix * x_pitch,
                    y = edge + hole_r
                        + (ix % 2) * y_pitch / 2
                        + iy * y_pitch
                )
                    if (
                        x + hole_r <= width - edge
                        && y + hole_r <= depth - edge
                    )
                        translate([x, y, -0.2])
                            cylinder(
                                r = hole_r,
                                h = thickness + 0.4,
                                $fn = 6
                            );
    }
}

module vented_base() {
    honeycomb_plate(
        half_width,
        module_depth,
        base_thickness
    );
}

module front_panel(hand) {
    body_x = hand == "left"
        ? rack_ear_width + rack_ear_relief
        : 0;
    body_width = half_width - rack_ear_width - rack_ear_relief;
    ear_x = hand == "left" ? 0 : half_width - rack_ear_width;

    translate([body_x, 0, 0])
        cube([body_width, front_thickness, panel_height]);

    // A forward-stepped outer strip makes the integrated rack ear explicit.
    translate([
        ear_x,
        -rack_ear_forward,
        0
    ])
        cube([
            rack_ear_width,
            rack_ear_thickness,
            panel_height
        ]);

    // Three local bridges transfer screw loads while leaving visible reliefs.
    for (z = rack_hole_z) {
        bridge_x = hand == "left"
            ? rack_ear_width - 1
            : half_width - rack_ear_width - rack_ear_relief - 4;
        translate([bridge_x, 0, z - 4.25])
            cube([5 + rack_ear_relief, 7, 8.5]);
    }
}

module corner_posts() {
    wall = 3;
    cap = 3;

    for (x = [0, half_width - corner_size])
        for (y = [0, module_depth - corner_size])
            translate([x, y, 0]) {
                // Thin outer L-walls resist racking.
                translate([
                    x == 0 ? 0 : corner_size - wall,
                    0,
                    0
                ])
                    cube([wall, corner_size, panel_height]);
                translate([
                    0,
                    y == 0 ? 0 : corner_size - wall,
                    0
                ])
                    cube([corner_size, wall, panel_height]);

                // Solid caps support stack pegs, sockets and magnet pockets.
                cube([corner_size, corner_size, cap]);
                translate([0, 0, panel_height - cap])
                    cube([corner_size, corner_size, cap]);
            }
}

module stack_features_positive() {
    // Printed registration pegs carry shear; magnets only provide retention.
    for (p = [
        [13, 13],
        [half_width - 13, 13],
        [13, module_depth - 13],
        [half_width - 13, module_depth - 13]
    ])
        translate([p[0], p[1], panel_height])
            cylinder(d1 = 5.0, d2 = 4.6, h = 3.0);
}

module stack_feature_cuts() {
    // Bottom sockets.
    for (p = [
        [13, 13],
        [half_width - 13, 13],
        [13, module_depth - 13],
        [half_width - 13, module_depth - 13]
    ])
        translate([p[0], p[1], -0.2])
            cylinder(d = 5.0 + peg_clearance, h = 3.6);

    // 6x2 magnet pockets in the top and bottom of the corner posts.
    for (p = [
        [corner_size / 2, corner_size / 2],
        [half_width - corner_size / 2, corner_size / 2],
        [corner_size / 2, module_depth - corner_size / 2],
        [half_width - corner_size / 2, module_depth - corner_size / 2]
    ]) {
        translate([p[0], p[1], -0.2])
            cylinder(
                d = stack_magnet_d + magnet_clearance,
                h = stack_magnet_h + 0.25
            );
        translate([p[0], p[1], panel_height - stack_magnet_h - 0.05])
            cylinder(
                d = stack_magnet_d + magnet_clearance,
                h = stack_magnet_h + 0.25
            );
    }
}

module diamond_key_x(length, root_size, tip_size) {
    rotate([0, 90, 0])
        linear_extrude(
            height = length,
            scale = tip_size / root_size
        )
            polygon([
                [-root_size / 2, 0],
                [0, -root_size / 2],
                [root_size / 2, 0],
                [0, root_size / 2]
            ]);
}

module side_join_blocks(hand) {
    seam_x = hand == "left"
        ? half_width - side_join_tower_w
        : 0;

    for (y = side_join_y) {
        // A broad tower and inward 45-degree buttress carry the keys into the
        // floor instead of concentrating load in the former 4 mm web.
        translate([
            seam_x,
            y - side_join_tower_d / 2,
            0
        ])
            cube([
                side_join_tower_w,
                side_join_tower_d,
                panel_height
            ]);

        hull() {
            translate([
                hand == "left"
                    ? seam_x - side_join_gusset_run
                    : seam_x + side_join_tower_w,
                y - side_join_tower_d / 2,
                0
            ])
                cube([
                    side_join_gusset_run,
                    side_join_tower_d,
                    2.4
                ]);
            translate([
                seam_x,
                y - side_join_tower_d / 2,
                0
            ])
                cube([
                    side_join_tower_w,
                    side_join_tower_d,
                    12
                ]);
        }

        for (z = [11, 33])
            translate([seam_x, y, z])
                diamond_key_x(
                    side_join_tower_w,
                    12,
                    12
                );

        translate([seam_x, y, 22])
            rotate([0, 90, 0])
                cylinder(
                    d = 12,
                    h = side_join_tower_w
                );
    }
}

module side_key_socket(length, clearance = peg_clearance) {
    diamond_key_x(
        length,
        side_key_root + clearance,
        side_key_tip + clearance
    );
}

module side_join_positive(hand) {
    // Broad 45-degree keys print without support and carry seam shear.
    if (hand == "left")
        for (y = side_join_y)
            for (z = [11, 33])
                translate([
                    half_width - 1.4,
                    y,
                    z
                ])
                    diamond_key_x(
                        side_key_length + 1.4,
                        side_key_root,
                        side_key_tip
                    );
}

module side_join_cuts(hand) {
    for (y = side_join_y) {
        if (hand == "left")
            translate([half_width - side_magnet_h - 0.05, y, 22])
                rotate([0, 90, 0])
                    cylinder(
                        d = side_magnet_d + magnet_clearance,
                        h = side_magnet_h + 0.25
                    );
        else
            translate([-0.2, y, 22])
                rotate([0, 90, 0])
                    cylinder(
                        d = side_magnet_d + magnet_clearance,
                        h = side_magnet_h + 0.25
                    );
    }

    if (hand == "right")
        for (y = side_join_y)
            for (z = [11, 33])
                translate([-0.2, y, z])
                    side_key_socket(
                        side_key_length + side_key_socket_extra
                    );
}

module rear_brace_cuts() {
    // Two sockets accept the printed desk spine's tapered pegs.
    for (x = [18, half_width - 18])
        translate([x, module_depth + 0.2, 22])
            rotate([90, 0, 0])
                cylinder(d = 5.0 + peg_clearance, h = 4.2);

    // 6x2 retention magnets above each rear socket.
    for (x = [18, half_width - 18])
        translate([x, module_depth + 0.2, 33])
            rotate([90, 0, 0])
                cylinder(
                    d = stack_magnet_d + magnet_clearance,
                    h = stack_magnet_h + 0.25
                );
}

module rear_brace_towers() {
    for (x = [18, half_width - 18]) {
        // C-channel tower carries bending with less material than a solid post.
        translate([x - 5, module_depth - 3, 0])
            cube([10, 3, panel_height]);
        translate([x - 5, module_depth - 6, 0])
            cube([2, 6, panel_height]);
        translate([x + 3, module_depth - 6, 0])
            cube([2, 6, panel_height]);

        // Local bosses provide full depth around the peg and magnet sockets.
        for (z = [22, 33])
            translate([x, module_depth, z])
                rotate([90, 0, 0])
                    cylinder(d = 9, h = 6);
    }
}

module common_positive(hand) {
    vented_base();
    front_panel(hand);
    translate([0, module_depth - rear_thickness, 0])
        cube([half_width, rear_thickness, 8]);
    corner_posts();
    side_join_blocks(hand);
    stack_features_positive();
    side_join_positive(hand);

    rear_brace_towers();

    // Side rails resist racking while keeping airflow open.
    translate([0, 0, 0])
        cube([3, module_depth, 6]);
    translate([half_width - 3, 0, 0])
        cube([3, module_depth, 6]);
}

module rack_hole_cuts(hand) {
    rack_x = hand == "left"
        ? rack_hole_edge
        : half_width - rack_hole_edge;

    for (z = rack_hole_z)
        rack_slot(rack_x, z);
}

module common_cuts(hand) {
    rack_hole_cuts(hand);
    stack_feature_cuts();
    side_join_cuts(hand);
    rear_brace_cuts();
    exposed_module_corner_chamfer_cuts(hand);
}

module device_rails(x, width, depth, height) {
    rail_h = min(height * 0.45, 13);

    translate([x - 2.2, front_thickness, base_thickness])
        cube([2.2, depth, rail_h]);
    translate([x + width, front_thickness, base_thickness])
        cube([2.2, depth, rail_h]);

    // Low rear stop does not block rear connectors.
    translate([x - 2.2, front_thickness + depth, base_thickness])
        cube([width + 4.4, 2.2, 4]);
}

module ucg_module(hand = "left") {
    device_x = hand == "left" ? 19 : half_width - 19 - ucg_size[0];
    keystone_start = hand == "left" ? 168 : 18;

    difference() {
        union() {
            common_positive(hand);
            device_rails(
                device_x,
                ucg_size[0] + fit_clearance,
                ucg_size[1] + fit_clearance,
                ucg_size[2]
            );
        }

        common_cuts(hand);
        face_cutout(
            device_x - 0.4,
            4.0,
            ucg_size[0] + fit_clearance + 0.8,
            ucg_size[2] + fit_clearance + 0.8
        );

        for (i = [0 : 2])
            keystone_cutout_at(keystone_start + i * 19);
    }
}

module usw_module(hand = "right") {
    device_x = hand == "right" ? 19.5 : 18.8;
    keystone_x = hand == "right"
        ? 2.0
        : half_width - 2.0 - keystone_cutout[0];

    difference() {
        union() {
            common_positive(hand);
            device_rails(
                device_x,
                usw_size[0] + fit_clearance,
                usw_size[1] + fit_clearance,
                usw_size[2]
            );
        }

        common_cuts(hand);
        face_cutout(
            device_x - 0.4,
            3.6,
            usw_size[0] + fit_clearance + 0.8,
            usw_size[2] + fit_clearance + 1.0
        );
        keystone_cutout_at(keystone_x);
    }
}

function bay_x(index) = bay_start + index * (bay_width + bay_gap);

module modular_bay_rails(index) {
    x = bay_x(index);
    rail_h = bay_opening_z - base_thickness;

    for (rail_x = [x + 1, x + bay_width - 4])
        translate([rail_x, front_thickness, base_thickness])
            cube([3, bay_depth, rail_h]);

    translate([
        x + 1,
        front_thickness + bay_depth - 3,
        base_thickness
    ])
        cube([bay_width - 2, 3, rail_h + 2]);

    // Long guide lips constrain the drawer after it enters the face opening.
    bay_guide_lips(x, bay_opening_z);
}

module dual_pi_module(hand = "left") {
    difference() {
        union() {
            common_positive(hand);
            for (index = [0 : bay_count - 1])
                modular_bay_rails(index);
        }

        common_cuts(hand);
        for (index = [0 : bay_count - 1]) {
            bay_face_cutout(
                bay_x(index),
                bay_opening_z
            );
            bay_service_detent_pockets(
                bay_x(index),
                bay_opening_z
            );
        }
    }
}

module pi_mount_positions() {
    board_x = (bay_width - pi_board[0]) / 2;
    board_y = 23;

    for (dx = pi_mount_pattern_x)
        for (dy = pi_mount_pattern_y)
            translate([board_x + dx, board_y + dy, 0])
                children();
}

module pi_cartridge_locators() {
    board_x = (bay_width - pi_board[0]) / 2;
    board_y = 23;
    locator_z = pi_mount_height + 1.0;
    tab_depth = 10;

    // Four side tabs carry shear without covering the PCB top.
    for (x = [
        board_x - pi_locator_clearance - 1.5,
        board_x + pi_board[0] + pi_locator_clearance
    ])
        for (y = [board_y + 8, board_y + 67])
            translate([x, y, 1.6])
                cube([1.5, tab_depth, locator_z - 1.6]);

    // Rear corner stops leave the central microSD access area open.
    for (x = [board_x + 1, board_x + pi_board[0] - 6])
        translate([
            x,
            board_y + pi_board[1] + pi_locator_clearance,
            1.6
        ])
            cube([5, 1.5, locator_z - 1.6]);
}

module pi_cartridge_mount(mount_variant = "magnetic") {
    board_x = (bay_width - pi_board[0]) / 2;
    board_y = 23;
    mount_z = 1.6;

    for (rail_y = [board_y - 1, board_y + 57])
        translate([board_x, rail_y, 0])
            cube([pi_board[0], 8, 3.4]);

    pi_mount_positions()
        translate([0, 0, mount_z])
            cylinder(
                d = pi_mount_boss_d,
                h = pi_mount_height - mount_z
            );

    if (mount_variant == "magnetic")
        pi_cartridge_locators();
    else
        for (x = [board_x - 1.5, board_x + pi_board[0]])
            translate([x, board_y - 2, 1.6])
                cube([1.5, pi_board[1] + 4, 5.2]);
}

module pi_cartridge_retention_cuts(
    mount_variant = "magnetic"
) {
    shoulder_z = pi_mount_height - pi_mount_shoulder;
    screw_head_bottom = pi_mount_height
        - pi_magnetic_assumed_screw_head_h;
    skin_top = screw_head_bottom - pi_magnetic_target_gap;
    skin_bottom = skin_top - pi_magnetic_insulating_skin;

    pi_mount_positions()
        if (mount_variant == "magnetic") {
            // Underside glue pocket. Hold the magnet against the printed roof
            // while epoxy cures, then fill the access recess flush if desired.
            translate([0, 0, -0.2])
                cylinder(
                    d = pi_magnet_pocket_d,
                    h = skin_bottom + 0.2
                );
            translate([0, 0, skin_top])
                cylinder(
                    d = pi_mount_head_clearance_d,
                    h = pi_mount_height - skin_top + 0.4
                );
        } else {
            translate([0, 0, -0.2])
                cylinder(
                    d = pi_mount_head_clearance_d,
                    h = shoulder_z + 0.2
                );
            translate([0, 0, shoulder_z])
                cylinder(
                    d = pi_mount_screw_d,
                    h = pi_mount_shoulder + 0.4
                );
        }
}

module pi_cartridge(
    label = "PI",
    installed = false,
    mount_variant = "magnetic"
) {
    tray_x = bay_clearance + 0.8;
    tray_w = bay_width - 2 * tray_x;
    flange_x = -1.25;
    flange_w = bay_width + 2.5;
    connector_w = 53.5;

    module geometry() {
        difference() {
            union() {
                translate([tray_x, 0, 0])
                    honeycomb_plate(
                        tray_w,
                        bay_depth,
                        1.8,
                        edge = 4,
                        cell_r = 8,
                        hole_r = 5.4
                    );
                translate([flange_x, -2.4, 0])
                    translate([0, 2.4, 0])
                        chamfered_front_flange(
                            flange_w,
                            2.4,
                            bay_opening_h
                        );
                translate([
                    bay_clearance,
                    0,
                    bay_clearance
                ])
                    cube([
                        bay_width - 2 * bay_clearance,
                        3.0,
                        bay_opening_h - 2 * bay_clearance
                    ]);
                pi_cartridge_mount(mount_variant);
                cartridge_service_detents();
            }

            pi_cartridge_retention_cuts(mount_variant);
            translate([
                (bay_width - connector_w) / 2,
                -2.6,
                4.0
            ])
                cube([
                    connector_w,
                    6.0,
                    bay_opening_h
                ]);
        }
    }

    if (installed)
        geometry();
    else
        translate([1.25, 2.4, 0])
            geometry();
}

module pi_review_hardware(mount_variant = "through_floor") {
    board_x = (bay_width - pi_board[0]) / 2;
    board_y = 23;
    board_z = pi_mount_height;
    shoulder_z = pi_mount_height - pi_mount_shoulder;
    screw_head_bottom = board_z
        - pi_magnetic_assumed_screw_head_h;
    skin_top = screw_head_bottom - pi_magnetic_target_gap;
    skin_bottom = skin_top - pi_magnetic_insulating_skin;
    magnet_bottom = skin_bottom - stack_magnet_h;
    standoff_z = board_z + pi_board[2];

    color([0.10, 0.48, 0.22])
        translate([board_x, board_y, board_z])
            cube(pi_board);

    pi_mount_positions() {
        color([0.72, 0.56, 0.22])
            translate([0, 0, standoff_z])
                cylinder(d = 5.0, h = 8.4, $fn = 6);

        if (mount_variant == "magnetic") {
            color([0.72, 0.74, 0.78]) {
                translate([0, 0, screw_head_bottom])
                    cylinder(
                        d = pi_magnetic_assumed_screw_head_d,
                        h = pi_magnetic_assumed_screw_head_h
                    );
                translate([0, 0, board_z])
                    cylinder(
                        d = 2.5,
                        h = pi_board[2] + 3.2
                    );
            }
            color([0.82, 0.16, 0.13])
                translate([0, 0, magnet_bottom])
                    cylinder(
                        d = stack_magnet_d,
                        h = stack_magnet_h
                    );
        } else
            color([0.72, 0.74, 0.78]) {
                translate([
                    0,
                    0,
                    shoulder_z - pi_magnetic_assumed_screw_head_h
                ])
                    cylinder(
                        d = pi_magnetic_assumed_screw_head_d,
                        h = pi_magnetic_assumed_screw_head_h
                    );
                translate([0, 0, shoulder_z])
                    cylinder(
                        d = 2.5,
                        h = pi_mount_shoulder
                            + pi_board[2]
                            + 3.2
                    );
            }
    }
}

module pi_mount_review_assembly(
    mount_variant = "through_floor",
    underside = false
) {
    module assembly() {
        color([0.72, 0.74, 0.78, 0.82])
            pi_cartridge(
                "REVIEW",
                false,
                mount_variant
            );
        translate([1.25, 2.4, 0])
            pi_review_hardware(mount_variant);
    }

    if (underside)
        rotate([180, 0, 0])
            assembly();
    else
        assembly();
}

module pi_mount_review_cutaway(
    mount_variant = "through_floor"
) {
    board_x = (bay_width - pi_board[0]) / 2;
    board_y = 23;
    mount_x = board_x + pi_mount_pattern_x[0];
    mount_y = board_y + pi_mount_pattern_y[0];

    scale([4, 4, 4])
        translate([-mount_x, -mount_y, 0]) {
            color([0.72, 0.74, 0.78, 0.82])
                intersection() {
                    pi_cartridge(
                        "REVIEW",
                        true,
                        mount_variant
                    );
                    translate([
                        mount_x - 6,
                        mount_y - 7,
                        -0.2
                    ])
                        cube([6.05, 14, 12]);
                }

            intersection() {
                pi_review_hardware(mount_variant);
                translate([
                    mount_x - 6,
                    mount_y - 7,
                    -0.2
                ])
                    cube([12, 14, 22]);
            }
        }
}

module vent_cartridge(installed = false) {
    flange_x = -1.25;
    flange_w = bay_width + 2.5;
    runner_right_x = bay_width - vent_runner_x - vent_runner_w;
    chevron_center_x = bay_width / 2;

    module geometry() {
        difference() {
            union() {
                translate([flange_x, -2.4, 0])
                    translate([0, 2.4, 0])
                        chamfered_front_flange(
                            flange_w,
                            2.4,
                            bay_opening_h
                        );
                translate([
                    bay_clearance,
                    0,
                    bay_clearance
                ])
                    cube([
                        bay_width - 2 * bay_clearance,
                        3.0,
                        bay_opening_h - 2 * bay_clearance
                    ]);

                // Taper the wider face flange into the bay-width body so the
                // flat print orientation never starts a long unsupported lip.
                for (side = [-1, 1])
                    translate([0, 0, bay_clearance])
                        linear_extrude(
                            height = bay_opening_h
                                - 2 * bay_clearance
                        )
                            polygon(
                                side < 0
                                    ? [
                                        [flange_x, 0],
                                        [bay_clearance, 0],
                                        [bay_clearance, 1.65]
                                    ]
                                    : [
                                        [flange_x + flange_w, 0],
                                        [
                                            bay_width - bay_clearance,
                                            0
                                        ],
                                        [
                                            bay_width - bay_clearance,
                                            1.65
                                        ]
                                    ]
                            );

                // Two L-section runners engage the same floor tracks and guide
                // lips as the Pi drawers without changing the face fit.
                for (runner_x = [vent_runner_x, runner_right_x]) {
                    translate([runner_x, 0, 0])
                        cube([
                            vent_runner_w,
                            vent_cartridge_depth,
                            vent_runner_floor_t
                        ]);
                    translate([
                        runner_x
                            + (
                                runner_x == vent_runner_x
                                    ? 0
                                    : vent_runner_w - 1.2
                            ),
                        0,
                        0
                    ])
                        cube([
                            1.2,
                            vent_cartridge_depth,
                            vent_runner_h
                        ]);
                }

                // A rear chevron ties both runners into a triangle. In the
                // face-down print orientation each leg grows inward from a
                // supported runner without a transverse bridge.
                for (side = [-1, 1])
                    hull() {
                        translate([
                            side < 0
                                ? vent_runner_x + vent_runner_w - vent_chevron_w
                                : runner_right_x,
                            vent_chevron_start_y,
                            0
                        ])
                            cube([
                                vent_chevron_w,
                                vent_chevron_w,
                                vent_runner_floor_t
                            ]);
                        translate([
                            chevron_center_x
                                + side * vent_chevron_w / 2
                                - vent_chevron_w / 2,
                            vent_chevron_peak_y,
                            0
                        ])
                            cube([
                                vent_chevron_w,
                                vent_chevron_w,
                                vent_runner_floor_t
                            ]);
                    }
                cartridge_service_detents();
            }

            for (x = [8 : 11 : bay_width - 8])
                for (z = [5, 14])
                    translate([x - 3.2, -2.6, z])
                        cube([6.4, 6.0, 7]);
        }

    }

    if (installed)
        geometry();
    else
        translate([1.25, 2.4, 0])
            geometry();
}

module installed_pi_cartridges() {
    translate([bay_x(0), 0, bay_opening_z])
        pi_cartridge("PI 1", true);
    translate([bay_x(1), 0, bay_opening_z])
        vent_cartridge(true);
    translate([bay_x(2), 0, bay_opening_z])
        pi_cartridge("PI 2", true);
}

module dual_pi_faceplate(installed = false) {
    pi_cartridge("PI 1", installed);
}

module blank_module(hand = "right") {
    difference() {
        common_positive(hand);
        common_cuts(hand);

        // Large airflow opening; the remaining border is useful for future parts.
        face_cutout(24, 8, half_width - 48, panel_height - 16);
    }
}

module uk_ultra_top() {
    cap_t = 4.0;
    vent_t = 1.8;
    device_w = uk_ultra_size[0] + uk_ultra_clearance;
    device_d = uk_ultra_size[1] + uk_ultra_clearance;
    device_x = (half_width - device_w) / 2;
    device_y = (module_depth - device_d) / 2;
    wall_h = 10;
    guide_len = 20;
    crossrail_w = 3.2;

    difference() {
        union() {
            // Vented top plate with solid corners for the stack interface.
            difference() {
                honeycomb_plate(
                    half_width,
                    module_depth,
                    vent_t
                );

                // Leave only a perimeter ledge beneath the access point.
                translate([device_x + 8, device_y + 8, -0.2])
                    cube([device_w - 16, device_d - 16, cap_t + 0.4]);

                // Cable route from the open underside to the rear edge.
                translate([
                    half_width / 2 - 22,
                    device_y + device_d - 8,
                    -0.2
                ])
                    cube([
                        44,
                        module_depth - device_y - device_d + 9,
                        cap_t + 0.4
                    ]);
            }

            // Full-height corner pads retain the unchanged peg and magnet
            // sockets while the ventilated field stays shell-thickness only.
            for (x = [0, half_width - corner_size])
                for (y = [0, module_depth - corner_size])
                    translate([x, y, 0])
                        cube([corner_size, corner_size, cap_t]);

            // Continuous support rails tie both cradle walls into the plate,
            // even where the ventilation slots pass beneath them.
            for (x = [device_x - 2.2, device_x + device_w])
                translate([x, device_y, 0])
                    cube([2.2, device_d, cap_t]);
            for (y = [
                device_y,
                device_y + device_d - crossrail_w
            ])
                translate([device_x - 2.2, y, 0])
                    cube([
                        device_w + 4.4,
                        crossrail_w,
                        cap_t
                    ]);

            // Four short guides locate the assembled AP plus its OEM keyed
            // cradle without covering unpublished RP-SMA positions.
            for (x = [device_x - 2.2, device_x + device_w])
                for (y = [
                    device_y + 5,
                    device_y + device_d - guide_len - 5
                ])
                    translate([x, y, cap_t - 0.2])
                        cube([2.2, guide_len, wall_h + 0.2]);

            // Corner end-stops leave the center of both short ends open for
            // PoE cabling and optional RP-SMA antennas.
            for (x = [device_x, device_x + device_w - 20]) {
                translate([x, device_y - 2.2, 0])
                    cube([20, 2.2, cap_t + 7]);
                translate([x, device_y + device_d, 0])
                    cube([20, 2.2, cap_t + 7]);
            }
        }

        // Receive the four pegs and 6x2 magnets from the top rack module.
        for (p = [
            [13, 13],
            [half_width - 13, 13],
            [13, module_depth - 13],
            [half_width - 13, module_depth - 13]
        ])
            translate([p[0], p[1], -0.2])
                cylinder(d = 5.0 + peg_clearance, h = 3.6);

        for (p = [
            [corner_size / 2, corner_size / 2],
            [half_width - corner_size / 2, corner_size / 2],
            [corner_size / 2, module_depth - corner_size / 2],
            [half_width - corner_size / 2, module_depth - corner_size / 2]
        ])
            translate([p[0], p[1], -0.2])
                cylinder(
                    d = stack_magnet_d + magnet_clearance,
                    h = stack_magnet_h + 0.25
                );

        rectangular_corner_chamfer_cuts(
            half_width,
            module_depth,
            cap_t + wall_h + 0.4
        );
    }
}

module desk_spine(units = 3) {
    spine_w = 14;
    spine_t = 5;
    web_t = 2.4;
    flange_w = 2.4;
    spine_h = units * u_height - (u_height - panel_height);

    difference() {
        union() {
            // C-channel resists side bending with less PLA than a solid bar.
            cube([spine_w, web_t, spine_h]);
            cube([flange_w, spine_t, spine_h]);
            translate([spine_w - flange_w, 0, 0])
                cube([flange_w, spine_t, spine_h]);

            // Tapered pegs enter each module's rear socket.
            for (u = [0 : units - 1])
                translate([spine_w / 2, -3.0, 22 + u * u_height])
                    rotate([-90, 0, 0])
                        cylinder(d1 = 4.6, d2 = 5.0, h = 3.2);
        }

        // 6x2 magnet pockets align with the module rear faces.
        for (u = [0 : units - 1])
            translate([spine_w / 2, -0.2, 33 + u * u_height])
                rotate([-90, 0, 0])
                    cylinder(
                        d = stack_magnet_d + magnet_clearance,
                        h = stack_magnet_h + 0.25
                    );
    }
}

module desk_spine_print(units = 4) {
    // Lay the spine flat; its retention pegs then print vertically upward.
    translate([0, 0, 5])
        rotate([-90, 0, 0])
            desk_spine(units);
}

module fit_test_coupon() {
    difference() {
        union() {
            // A shell-thickness carrier keeps every test feature connected
            // without creating a broad top skin over sparse infill.
            cube([70, 32, 1.8]);

            for (p = [
                [10, 10],
                [24, 10],
                [59, 10],
                [59, 24]
            ])
                translate([p[0], p[1], 0])
                    cylinder(d = 12, h = 6);

            translate([33, 4, 0])
                cube([
                    keystone_cutout[0] + 6,
                    keystone_cutout[1] + 6,
                    6
                ]);
        }

        // Production glue-fit pocket plus a tighter diagnostic pocket.
        translate([10, 10, 3.8])
            cylinder(d = 6 + magnet_clearance, h = 2.4);
        translate([24, 10, 3.8])
            cylinder(d = 6 + 0.10, h = 2.4);
        translate([36, 7, -0.2])
            cube([
                keystone_cutout[0],
                keystone_cutout[1] + keystone_top_clearance,
                6.4
            ]);
        translate([59, 10, -0.2])
            cylinder(d = 5 + peg_clearance, h = 6.4);
    }

    translate([59, 24, 6])
        cylinder(d1 = 5.0, d2 = 4.6, h = 3.0);
}

module rack_ear_fit_test() {
    difference() {
        cube([
            rack_ear_width,
            rack_ear_thickness,
            panel_height
        ]);
        for (z = rack_hole_z)
            rack_slot(rack_hole_edge, z);
    }
}

module rack_ear_fit_test_print() {
    translate([0, 0, rack_ear_thickness])
        rotate([-90, 0, 0])
            rack_ear_fit_test();
}

module bay_fit_test() {
    union() {
        difference() {
            union() {
                cube([
                    bay_width + 8,
                    6,
                    bay_opening_h + 8
                ]);
                for (rail_x = [5, bay_width])
                    translate([rail_x, 5.8, 0])
                        cube([
                            3,
                            bay_fit_coupon_depth - 5.8,
                            4
                        ]);
                for (side_x = [0, bay_width + 4])
                    translate([side_x, 5.8, 12])
                        cube([4, 16.2, 14]);
            }
            bay_face_cutout(4, 4);
            translate([4, faceplate_chamfer, 4])
                cube([
                    bay_width,
                    bay_fit_coupon_depth,
                    bay_opening_h
                ]);
            bay_service_detent_pockets(4, 4);
        }
        bay_guide_lips(
            4,
            4,
            face_clearance_depth,
            bay_fit_coupon_depth - face_clearance_depth
        );
    }
}

module bay_fit_test_print() {
    translate([0, bay_opening_h + 8, 0])
        rotate([90, 0, 0])
            bay_fit_test();
}

module vent_cartridge_print() {
    translate([
        0,
        bay_opening_h,
        0
    ])
        rotate([90, 0, 0])
            vent_cartridge(false);
}

module side_key_male_test() {
    union() {
        cube([8, 16, 12]);
        translate([6.6, 8, 6])
            diamond_key_x(
                side_key_length + 1.4,
                side_key_root,
                side_key_tip
            );
    }
}

module side_key_socket_test() {
    difference() {
        cube([8, 16, 12]);
        translate([-0.2, 8, 6])
            side_key_socket(
                side_key_length + side_key_socket_extra
            );
    }
}

module side_tower_male_test() {
    translate([-220, -38, 0])
        intersection() {
            union() {
                side_join_blocks("left");
                side_join_positive("left");
            }
            translate([220, 38, -0.2])
                cube([25, 16, panel_height + 3.4]);
        }
}

module side_tower_socket_test() {
    translate([1, -38, 0])
        intersection() {
            difference() {
                side_join_blocks("right");
                side_join_cuts("right");
            }
            translate([-1, 38, -0.2])
                cube([20, 16, panel_height + 0.4]);
        }
}

module rounded_prism(width, depth, height, radius) {
    hull()
        for (x = [radius, width - radius])
            for (y = [radius, depth - radius])
                translate([x, y, 0])
                    cylinder(r = radius, h = height);
}

module desktop_foot(magnet_xy, peg_xy) {
    difference() {
        hull() {
            rounded_prism(22, 22, 2.4, 3);
            translate([2, 2, 2.4])
                rounded_prism(18, 18, 3.6, 2.5);
        }

        // Optional recess for a common adhesive felt/rubber pad.
        translate([11, 11, -0.2])
            cylinder(d = 16, h = 1.0);

        translate([magnet_xy[0], magnet_xy[1], 3.75])
            cylinder(
                d = stack_magnet_d + magnet_clearance,
                h = stack_magnet_h + 0.45
            );
    }

    translate([peg_xy[0], peg_xy[1], 5.8])
        cylinder(d1 = 5.0, d2 = 4.6, h = 3.2);
}

module magnet_polarity_key() {
    difference() {
        union() {
            rounded_prism(50, 18, 1.8, 3);
            translate([9, 9, 0])
                cylinder(d = 14, h = 4);
        }
        translate([9, 9, 1.75])
            cylinder(
                d = stack_magnet_d + magnet_clearance,
                h = stack_magnet_h + 0.45
            );
    }

    translate([31, 9, 1.8])
        linear_extrude(height = 0.6)
            text(
                "UP",
                size = 5,
                halign = "center",
                valign = "center"
            );
    translate([18, 6, 1.8])
        linear_extrude(height = 0.6)
            polygon([[0, 0], [6, 3], [0, 6]]);
}

module desktop_feet_set() {
    translate([0, 0, 0])
        desktop_foot([8, 8], [13, 13]);
    translate([28, 0, 0])
        desktop_foot([14, 8], [9, 13]);
    translate([0, 28, 0])
        desktop_foot([8, 14], [13, 9]);
    translate([28, 28, 0])
        desktop_foot([14, 14], [9, 9]);

    // Peel-away sprues keep the four corner-specific feet together.
    translate([10, 21, 0])
        cube([30, 1.2, 1.0]);
    translate([10, 28, 0])
        cube([30, 1.2, 1.0]);
    translate([21, 10, 0])
        cube([1.2, 30, 1.0]);
    translate([28, 10, 0])
        cube([1.2, 30, 1.0]);
}

module installed_desktop_feet() {
    translate([0, 0, -5.8])
        desktop_foot([8, 8], [13, 13]);
    translate([half_width - 22, 0, -5.8])
        desktop_foot([14, 8], [9, 13]);
    translate([0, module_depth - 22, -5.8])
        desktop_foot([8, 14], [13, 9]);
    translate([
        half_width - 22,
        module_depth - 22,
        -5.8
    ])
        desktop_foot([14, 14], [9, 9]);
}

module production_test_plate() {
    // Spread the coupons across a nearly full bed so the slicer keeps this as
    // a dedicated first plate instead of packing them beside production parts.
    translate([8, 8, 0])
        fit_test_coupon();
    translate([95, 8, 0])
        rack_ear_fit_test_print();
    translate([166, 8, 0])
        bay_fit_test_print();
    translate([166, 62, 0])
        vent_cartridge_print();
    translate([8, 70, 0])
        side_key_male_test();
    translate([32, 70, 0])
        side_key_socket_test();
    translate([8, 145, 0])
        side_tower_male_test();
    translate([62, 145, 0])
        side_tower_socket_test();

    // Four removable feet match every possible bottom-module corner.
    translate([90, 65, 0])
        desktop_foot([8, 8], [13, 13]);
    translate([118, 65, 0])
        desktop_foot([14, 8], [9, 13]);
    translate([90, 95, 0])
        desktop_foot([8, 14], [13, 9]);
    translate([118, 95, 0])
        desktop_foot([14, 14], [9, 9]);
    translate([90, 130, 0])
        magnet_polarity_key();

    // Peel-away links make the coupon layout one reliable slicer object.
    translate([6, 7.2, 0])
        cube([229, 1.2, 1.0]);
    for (x = [15, 34, 65, 100, 128, 168, 232])
        translate([x, 7.2, 0])
            cube([1.2, x == 232 ? 193.8 : 153.8, 1.0]);
    translate([8, 145, 0])
        cube([132, 1.2, 1.0]);

    // Connected corner tab reserves the plate envelope without real waste.
    translate([232, 198, 0])
        cube([3, 3, 1.2]);
}

module side_join_preview() {
    color([0.12, 0.38, 0.72]) {
        translate([-half_width + 6, 0, 0]) {
            side_join_blocks("left");
            side_join_positive("left");
        }
    }

    color([0.55, 0.58, 0.62])
        translate([13, 0, 0])
            difference() {
                side_join_blocks("right");
                side_join_cuts("right");
            }
}

module modular_bay_preview() {
    color([0.16, 0.18, 0.22])
        dual_pi_module("left");
    color([0.08, 0.09, 0.12])
        installed_pi_cartridges();
    dummy_bay_labels();
    dummy_pis();
}

module arrow_y(length = 18, diameter = 2.2) {
    rotate([-90, 0, 0]) {
        cylinder(d = diameter, h = length - 4);
        translate([0, 0, length - 4])
            cylinder(d1 = diameter * 2.2, d2 = 0, h = 4);
    }
}

module vent_cutaway_chassis() {
    difference() {
        intersection() {
            dual_pi_module("left");
            translate([
                bay_x(1) - 6,
                -3,
                0
            ])
                cube([
                    bay_width + 12,
                    82,
                    panel_height
                ]);
        }
        translate([
            bay_x(1) + bay_width / 2,
            8,
            bay_opening_z + 8
        ])
            cube([
                bay_width,
                76,
                panel_height
            ]);
    }
}

module vent_cartridge_cutaway_preview() {
    state_spacing = bay_width + 34;

    for (state = [0, 1])
        translate([state * state_spacing, 0, 0]) {
            color([0.55, 0.58, 0.64, 0.55])
                vent_cutaway_chassis();

            color(
                state == 0
                    ? [0.12, 0.48, 0.78]
                    : [0.12, 0.62, 0.34]
            )
                translate([
                    bay_x(1),
                    state == 0 ? -25 : 0,
                    bay_opening_z
                ])
                    vent_cartridge(true);

            color(
                state == 0
                    ? [0.12, 0.70, 0.30]
                    : [0.92, 0.42, 0.08]
            )
                translate([
                    bay_x(1) + bay_width / 2,
                    state == 0 ? -34 : -5,
                    bay_opening_z + bay_opening_h + 4
                ])
                    if (state == 0)
                        arrow_y(22);
                    else
                        rotate([180, 0, 0])
                            arrow_y(18);

            color([0.12, 0.13, 0.16])
                translate([
                    bay_x(1) + bay_width / 2,
                    -8,
                    bay_opening_z + bay_opening_h + 10
                ])
                    rotate([90, 0, 0])
                        linear_extrude(height = 0.5)
                            text(
                                state == 0
                                    ? "PUSH TO CLICK"
                                    : "PULL EVENLY",
                                size = 4,
                                halign = "center",
                                valign = "center"
                            );
        }
}

module dummy_front_label(label, center_x, front_y, center_z, size = 5) {
    color([0.12, 0.13, 0.15])
        translate([center_x, front_y, center_z])
            rotate([90, 0, 0])
                linear_extrude(height = 0.5)
                    text(
                        label,
                        size = size,
                        halign = "center",
                        valign = "center"
                    );
}

module dummy_bay_labels() {
    labels = ["PI 1", "VENT", "PI 2"];

    for (index = [0 : bay_count - 1])
        color([0.72, 0.73, 0.76])
            translate([
                bay_x(index) + bay_width / 2,
                -2.6,
                bay_opening_z + 26.5
            ])
                rotate([90, 0, 0])
                    linear_extrude(height = 0.5)
                        text(
                            labels[index],
                            size = 3.3,
                            halign = "center",
                            valign = "center"
                        );
}

module dummy_keystone_at(cutout_x, cutout_z = 13.7) {
    body_x = cutout_x - (keystone_body[0] - keystone_cutout[0]) / 2;
    body_z = cutout_z - (keystone_body[2] - keystone_cutout[1]) / 2;
    flange_w = 18;
    flange_h = 20;

    color([0.48, 0.49, 0.52])
        translate([body_x, 0, body_z])
            cube(keystone_body);
    color([0.66, 0.67, 0.69])
        translate([
            cutout_x - (flange_w - keystone_cutout[0]) / 2,
            -1.5,
            cutout_z - (flange_h - keystone_cutout[1]) / 2
        ])
            cube([flange_w, 2, flange_h]);
}

module dummy_ucg_keystones(hand = "left") {
    start = hand == "left" ? 168 : 18;
    for (i = [0 : 2])
        dummy_keystone_at(start + i * 19);
}

module dummy_usw_keystone(hand = "right") {
    x = hand == "right"
        ? 2.0
        : half_width - 2.0 - keystone_cutout[0];
    dummy_keystone_at(x);
}

module dummy_ucg(hand = "left") {
    x = hand == "left" ? 19 : half_width - 19 - ucg_size[0];
    color([0.92, 0.92, 0.94])
        translate([x, front_thickness, base_thickness])
            cube(ucg_size);
    dummy_front_label(
        "UCG-ULTRA",
        x + ucg_size[0] / 2,
        front_thickness - 0.1,
        base_thickness + ucg_size[2] / 2,
        5.5
    );
}

module dummy_usw(hand = "right") {
    x = hand == "right" ? 19.5 : 18.8;
    color([0.90, 0.90, 0.92])
        translate([x, front_thickness, base_thickness])
            cube(usw_size);
    dummy_front_label(
        "USW-ULTRA",
        x + usw_size[0] / 2,
        front_thickness - 0.1,
        base_thickness + usw_size[2] / 2,
        5.5
    );
}

module dummy_pis() {
    board_x = [
        bay_x(0) + (bay_width - pi_board[0]) / 2,
        bay_x(2) + (bay_width - pi_board[0]) / 2
    ];

    for (x = board_x) {
        color([0.12, 0.50, 0.24])
            translate([
                x,
                23,
                bay_opening_z + 1.6 + 5.2
            ])
                cube(pi_board);
        color([0.08, 0.20, 0.45])
            translate([
                x,
                23,
                bay_opening_z + 1.6 + 15.2
            ])
                cube([poe_hat_plan[0], poe_hat_plan[1], 1.6]);
    }
}

module dummy_uk_ultra() {
    device_x = (half_width - uk_ultra_size[0]) / 2;
    device_y = (module_depth - uk_ultra_size[1]) / 2;

    color([0.86, 0.87, 0.89])
        translate([device_x, device_y, 4])
            cube(uk_ultra_size);
    dummy_front_label(
        "UK-ULTRA",
        device_x + uk_ultra_size[0] / 2,
        device_y - 0.1,
        4 + uk_ultra_size[2] / 2,
        6
    );
}

module desk_preview() {
    color([0.08, 0.09, 0.11])
        installed_desktop_feet();

    color([0.16, 0.18, 0.22])
        ucg_module("left");
    dummy_ucg("left");
    dummy_ucg_keystones("left");

    translate([0, 0, u_height]) {
        color([0.16, 0.18, 0.22])
            usw_module("right");
        dummy_usw("right");
        dummy_usw_keystone("right");
    }

    translate([0, 0, 2 * u_height]) {
        color([0.16, 0.18, 0.22])
            usw_module("left");
        dummy_usw("left");
        dummy_usw_keystone("left");
    }

    translate([0, 0, 3 * u_height]) {
        color([0.16, 0.18, 0.22])
            dual_pi_module("left");
        color([0.08, 0.09, 0.12])
            installed_pi_cartridges();
        dummy_bay_labels();
        dummy_pis();
    }

    translate([0, 0, 4 * u_height]) {
        color([0.10, 0.12, 0.16])
            uk_ultra_top();
        dummy_uk_ultra();
    }

    // Rear brace pair.
    color([0.08, 0.09, 0.11]) {
        translate([11, module_depth, 0])
            desk_spine(4);
        translate([half_width - 25, module_depth, 0])
            desk_spine(4);
    }
}

module rack_preview() {
    color([0.16, 0.18, 0.22])
        ucg_module("left");
    dummy_ucg("left");
    dummy_ucg_keystones("left");

    translate([half_width, 0, 0]) {
        color([0.16, 0.18, 0.22])
            usw_module("right");
        dummy_usw("right");
        dummy_usw_keystone("right");
    }

    translate([0, 0, u_height]) {
        color([0.16, 0.18, 0.22])
            usw_module("left");
        dummy_usw("left");
        dummy_usw_keystone("left");
    }

    translate([half_width, 0, u_height]) {
        color([0.16, 0.18, 0.22])
            usw_module("right");
        dummy_usw("right");
        dummy_usw_keystone("right");
    }

    translate([0, 0, 2 * u_height]) {
        color([0.16, 0.18, 0.22])
            dual_pi_module("left");
        color([0.08, 0.09, 0.12])
            installed_pi_cartridges();
        dummy_bay_labels();
        dummy_pis();
    }

    translate([half_width, 0, 2 * u_height])
        color([0.16, 0.18, 0.22])
            blank_module("right");
}

if (part == "ucg_left")
    ucg_module("left");
else if (part == "ucg_right")
    ucg_module("right");
else if (part == "usw_left")
    usw_module("left");
else if (part == "usw_right")
    usw_module("right");
else if (part == "dual_pi_left")
    dual_pi_module("left");
else if (part == "dual_pi_right")
    dual_pi_module("right");
else if (part == "dual_pi_faceplate")
    dual_pi_faceplate(false);
else if (part == "pi_cartridge_1")
    pi_cartridge("PI 1", false);
else if (part == "pi_cartridge_2")
    pi_cartridge("PI 2", false);
else if (part == "pi_mount_review_magnetic_stl")
    pi_cartridge("REVIEW A", false, "magnetic");
else if (part == "pi_mount_review_mechanical_stl")
    pi_cartridge("REVIEW B", false, "through_floor");
else if (part == "pi_mount_review_magnetic_cutaway")
    pi_mount_review_cutaway("magnetic");
else if (part == "pi_mount_review_mechanical_cutaway")
    pi_mount_review_cutaway("through_floor");
else if (part == "pi_mount_review_magnetic_underside")
    pi_mount_review_assembly("magnetic", true);
else if (part == "pi_mount_review_mechanical_underside")
    pi_mount_review_assembly("through_floor", true);
else if (part == "vent_cartridge")
    vent_cartridge_print();
else if (part == "blank_left")
    blank_module("left");
else if (part == "blank_right")
    blank_module("right");
else if (part == "uk_ultra_top")
    uk_ultra_top();
else if (part == "desk_spine")
    desk_spine_print(4);
else if (part == "desk_spine_4u")
    desk_spine_print(4);
else if (part == "desk_spine_5u")
    desk_spine_print(5);
else if (part == "fit_test")
    fit_test_coupon();
else if (part == "rack_ear_fit_test")
    rack_ear_fit_test_print();
else if (part == "bay_fit_test")
    bay_fit_test_print();
else if (part == "side_key_male_test")
    side_key_male_test();
else if (part == "side_key_socket_test")
    side_key_socket_test();
else if (part == "side_tower_male_test")
    side_tower_male_test();
else if (part == "side_tower_socket_test")
    side_tower_socket_test();
else if (part == "desktop_feet_set")
    desktop_feet_set();
else if (part == "installed_desktop_feet")
    installed_desktop_feet();
else if (part == "magnet_polarity_key")
    magnet_polarity_key();
else if (part == "production_test_plate")
    production_test_plate();
else if (part == "side_join_preview")
    side_join_preview();
else if (part == "modular_bay_preview")
    modular_bay_preview();
else if (part == "vent_cartridge_cutaway_preview")
    vent_cartridge_cutaway_preview();
else if (part == "rack_preview")
    rack_preview();
else
    desk_preview();
