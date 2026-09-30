"""Create the five-plate no-test project from the validated six-plate project."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
PROD = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
ET.register_namespace("", CORE)
ET.register_namespace("p", PROD)

PLATE_PITCH = 307.2
PLATE_COLUMNS = 3

# Object IDs are stable in the tracked six-plate project.
PLATES = {
    1: [22, 4],
    2: [24, 6],
    3: [26, 12],
    4: [28, 34],
    5: [30, 32, 8],
}
RENAMES = {
    4: "09_Rear_Spine_A.stl",
    6: "10_Rear_Spine_B.stl",
    12: "07_Vent_Insert.stl",
}

# Global transforms on Bambu Studio's 307.2 mm virtual plate grid.
TRANSFORMS = {
    22: "1 0 0 0 1 0 0 0 1 128 128 23.3500004",
    4: "0 -1 0 1 0 0 0 0 1 128 18 4",
    24: "1 0 0 0 1 0 0 0 1 435.2 128 23.3500004",
    6: "0 -1 0 1 0 0 0 0 1 435.2 18 4",
    26: "1 0 0 0 1 0 0 0 1 742.4 128 23.3500004",
    12: "1 0 0 0 1 0 0 0 1 742.4 17.5 56.6999969",
    28: "1 0 0 0 1 0 0 0 1 128.007247 -146.587347 23.3500004",
    34: "-2.22044605e-16 -1 0 1 -2.22044605e-16 0 0 0 1 127.206465 -256.436937 15",
    30: "1 0 0 0 1 0 0 0 1 440.549995 -145.949999 7",
    32: "-2.22044605e-16 -1 0 1 -2.22044605e-16 0 0 0 1 366.400006 -255.2 15",
    8: "1 0 0 0 1 0 0 0 1 517.2 -267.2 4.5",
}


def metadata(node: ET.Element, key: str) -> ET.Element:
    found = node.find(f"./metadata[@key='{key}']")
    if found is None:
        raise ValueError(f"Missing metadata {key}")
    return found


def encoded(root: ET.Element) -> bytes:
    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def encoded_relationships(root: ET.Element) -> bytes:
    ET.register_namespace("", REL)
    try:
        return encoded(root)
    finally:
        ET.register_namespace("", CORE)


def plate_origin(index: int) -> tuple[float, float]:
    zero_based = index - 1
    return (
        (zero_based % PLATE_COLUMNS) * PLATE_PITCH,
        -(zero_based // PLATE_COLUMNS) * PLATE_PITCH,
    )


def local_translation(transform: str, plate: int) -> tuple[float, float, float]:
    values = [float(value) for value in transform.split()]
    origin_x, origin_y = plate_origin(plate)
    return values[9] - origin_x, values[10] - origin_y, values[11]


def create_project(source: Path, output: Path) -> None:
    with ZipFile(source) as archive:
        entries = {name: archive.read(name) for name in archive.namelist()}

    settings = ET.fromstring(entries["Metadata/model_settings.config"])
    model = ET.fromstring(entries["3D/3dmodel.model"])
    required_ids = {object_id for ids in PLATES.values() for object_id in ids}

    names = {
        int(node.attrib["id"]): metadata(node, "name").attrib["value"]
        for node in settings.findall("object")
    }
    if set(TRANSFORMS) != required_ids:
        raise ValueError("Every required object must have exactly one transform")
    if not required_ids.issubset(names):
        raise ValueError("Tracked project object IDs changed; layout requires review")

    for node in list(settings.findall("object")):
        object_id = int(node.attrib["id"])
        if object_id not in required_ids:
            settings.remove(node)
            continue
        if object_id in RENAMES:
            for item in node.findall(".//metadata"):
                if item.attrib.get("key") in {"name", "source_file"}:
                    item.attrib["value"] = RENAMES[object_id]
    for node in list(settings.findall("plate")):
        settings.remove(node)

    assemble = settings.find("assemble")
    if assemble is None:
        raise ValueError("Project has no assemble metadata")
    for node in list(assemble):
        assemble.remove(node)

    identify_ids: dict[int, str] = {}
    for old_plate in ET.fromstring(
        entries["Metadata/model_settings.config"]
    ).findall("plate"):
        for instance in old_plate.findall("model_instance"):
            object_id = int(metadata(instance, "object_id").attrib["value"])
            identify_ids[object_id] = metadata(
                instance, "identify_id"
            ).attrib["value"]

    insert_at = list(settings).index(assemble)
    for plate_index, object_ids in PLATES.items():
        plate = ET.Element("plate")
        for key, value in [
            ("plater_id", str(plate_index)),
            ("plater_name", ""),
            ("locked", "false"),
            ("filament_map_mode", "Auto For Flush"),
            ("filament_maps", "1"),
            ("filament_volume_maps", "0"),
        ]:
            ET.SubElement(plate, "metadata", key=key, value=value)
        for object_id in object_ids:
            instance = ET.SubElement(plate, "model_instance")
            ET.SubElement(
                instance, "metadata", key="object_id", value=str(object_id)
            )
            ET.SubElement(
                instance, "metadata", key="instance_id", value="0"
            )
            ET.SubElement(
                instance,
                "metadata",
                key="identify_id",
                value=identify_ids[object_id],
            )
        settings.insert(insert_at, plate)
        insert_at += 1

    for object_id in [item for ids in PLATES.values() for item in ids]:
        ET.SubElement(
            assemble,
            "assemble_item",
            object_id=str(object_id),
            instance_id="0",
            transform=TRANSFORMS[object_id],
            offset="0 0 0",
        )
        ET.SubElement(
            assemble,
            "assemble_item",
            object_id=str(object_id),
            volume_id="0",
            transform="1 0 0 0 1 0 0 0 1 0 0 0",
        )

    resources = model.find(f"{{{CORE}}}resources")
    build = model.find(f"{{{CORE}}}build")
    if resources is None or build is None:
        raise ValueError("Invalid 3MF model")

    component_paths: dict[int, str] = {}
    for obj in list(resources):
        object_id = int(obj.attrib["id"])
        if object_id not in required_ids:
            resources.remove(obj)
            continue
        component = obj.find(
            f"./{{{CORE}}}components/{{{CORE}}}component"
        )
        if component is not None:
            component_paths[object_id] = component.attrib[
                f"{{{PROD}}}path"
            ].lstrip("/")

    for item in list(build):
        object_id = int(item.attrib["objectid"])
        if object_id not in required_ids:
            build.remove(item)
        else:
            item.attrib["transform"] = TRANSFORMS[object_id]

    entries["3D/3dmodel.model"] = encoded(model)
    entries["Metadata/model_settings.config"] = encoded(settings)
    entries["Metadata/slice_info.config"] = (
        b'<?xml version="1.0" encoding="UTF-8"?>\n'
        b"<config><header>"
        b'<header_item key="X-BBL-Client-Type" value="slicer"/>'
        b'<header_item key="X-BBL-Client-Version" value="02.08.02.61"/>'
        b"</header></config>\n"
    )
    entries["Metadata/filament_sequence.json"] = json.dumps(
        {f"plate_{index}": [1] for index in PLATES},
        separators=(",", ":"),
    ).encode("utf-8")
    project_settings = json.loads(
        entries["Metadata/project_settings.config"]
    )
    project_settings.update(
        {
            "enable_support": "0",
            "brim_type": "no_brim",
            "brim_width": "0",
            "skirt_loops": "0",
        }
    )
    entries["Metadata/project_settings.config"] = json.dumps(
        project_settings,
        separators=(",", ":"),
    ).encode("utf-8")

    kept_model_paths = set(component_paths.values())
    for name in list(entries):
        if name.startswith("3D/Objects/") and name not in kept_model_paths:
            del entries[name]
        elif re.fullmatch(
            r"Metadata/(?:plate|plate_no_light|top|pick)_\d+"
            r"(?:_small)?\.(?:png|json)",
            name,
        ):
            del entries[name]
        elif re.fullmatch(r"Metadata/plate_\d+\.gcode(?:\.md5)?", name):
            del entries[name]

    # Bambu Studio regenerates these links when it writes the sliced project.
    entries.pop("Metadata/_rels/model_settings.config.rels", None)

    rels_name = "3D/_rels/3dmodel.model.rels"
    if rels_name in entries:
        rels = ET.fromstring(entries[rels_name])
        for relation in list(rels):
            target = relation.attrib.get("Target", "").lstrip("/")
            if target.startswith("3D/Objects/") and target not in kept_model_paths:
                rels.remove(relation)
        entries[rels_name] = encoded_relationships(rels)

    root_rels = ET.fromstring(entries["_rels/.rels"])
    for relation in list(root_rels):
        if relation.attrib.get("Target") != "/3D/3dmodel.model":
            root_rels.remove(relation)
    entries["_rels/.rels"] = encoded_relationships(root_rels)

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    with ZipFile(
        temporary, "w", compression=ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for name, data in entries.items():
            archive.writestr(name, data)
    temporary.replace(output)

    print(f"Created {output} with {len(required_ids)} objects on 5 plates:")
    for plate_index, object_ids in PLATES.items():
        listed = ", ".join(
            RENAMES.get(object_id, names[object_id])
            for object_id in object_ids
        )
        print(f"  Plate {plate_index}: {listed}")
        for object_id in object_ids:
            local = local_translation(TRANSFORMS[object_id], plate_index)
            print(
                f"    {RENAMES.get(object_id, names[object_id])} "
                f"center: {local}"
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    create_project(args.source, args.output)


if __name__ == "__main__":
    main()
