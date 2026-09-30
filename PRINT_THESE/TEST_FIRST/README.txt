PRINT PLATE 1 FIRST
===================

Open plate_1-test.3mf. It stores plate 1 as independently arranged objects, so
every coupon and useful part remains inside the A1 build area and can be moved
or removed individually.

Plate 1 validates the important fits before committing 21h15m21s and 479.32 g
of PLA to production plates 2-6:

- 6 x 2 mm production glue-fit magnet pocket
- Tighter 6 x 2 mm diagnostic magnet pocket
- Stack registration peg and socket, each shown with its associated 6 x 2 mm
  magnet-pocket position
- Reinforced side tower, diamond key, and matching socket
- Rack-ear slots
- Keystone cutout
- Pi-bay opening, receiving chamfer, service detents, guide lips, and
  removable full-depth vent cartridge
- Four removable desktop feet with optional 16 mm felt/rubber-pad recesses
- "UP" magnet polarity reference key

Use the normal production profile. Glue is still recommended for final magnet
installation even if the tighter diagnostic pocket appears to hold by friction.

The peg and socket are independent gauges on the connected card and cannot
mate to each other. Their adjacent pockets reproduce the exact production
offset on the top and bottom faces, making the four-pair stack pattern
unambiguous. The standalone pockets still validate production and tighter
diagnostic diameters.

Magnet orientation:

1. Choose either face of one magnet and mark it with a permanent marker.
2. Glue that magnet into the polarity key with the marked face visible beside
   the "UP" label.
3. Use the key to orient every loose magnet, marking the matching upward face.
4. Install stack and foot magnets with the marked face globally upward (+Z).
   On top pockets the mark remains visible; on bottom pockets it points into
   the part.
5. Install rear module/spine magnets with the marked face toward the rack rear
   (+Y). Install future side-seam magnets toward rack right (+X).
6. Pi magnet polarity does not affect steel attraction; marked face upward is
   preferred for consistency.

The feet are corner-specific because the peg and magnet have different offsets.
They only seat fully at the correct corner; never force them.

The included native plate keeps all parts axis-aligned and independently
selectable. Its longest slicer-classified bridge is 18.84 mm. The fit coupon's
functional features are carried by local bosses on a thin connected base, and
the polarity key uses a local magnet boss, avoiding broad unsupported top
skins.

Insert the vent through the coupon before printing the chassis. Confirm that
the runners enter the guide lips without binding, both detents click, the face
seats flush, and an even pull releases it without tools.

Do not continue with plates 2-6 if the peg, key, bay insert, keystone, or magnet
fit requires excessive force. Adjust the corresponding clearance in
homelab_rack.scad and regenerate the project first.
