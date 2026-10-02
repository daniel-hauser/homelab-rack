"""Create the consolidated single-plate Pi replacement project."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import json
import re
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
PROD = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
ET.register_namespace("", CORE)
ET.register_namespace("p", PROD)

CHASSIS_TRANSFORM = "1 0 0 0 1 0 0 0 1 5.75 12 -1.85302724e-08"
DRAWER_TRANSFORMS = {
    "05_Pi_Drawer_1_6mm_Magnet_Fit.stl":
        "0 -1 0 1 0 0 0 0 1 10 235 0",
    "06_Pi_Drawer_2_6mm_Magnet_Fit.stl":
        "0 -1 0 1 0 0 0 0 1 131.6 235 0",
}
ID_OFFSET = 10
PATHS = {
    "3D/Objects/object_1.model": "3D/Objects/object_11.model",
    "3D/Objects/object_2.model": "3D/Objects/object_12.model",
}


def encoded(root: ET.Element) -> bytes:
    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def encoded_relationships(root: ET.Element) -> bytes:
    ET.register_namespace("", REL)
    try:
        return encoded(root)
    finally:
        ET.register_namespace("", CORE)


def metadata(node: ET.Element, key: str) -> ET.Element:
    found = node.find(f"./metadata[@key='{key}']")
    if found is None:
        raise ValueError(f"Missing metadata {key}")
    return found


def shift_ids(root: ET.Element) -> None:
    for node in root.iter():
        if "id" in node.attrib and node.tag.endswith("object"):
            node.attrib["id"] = str(int(node.attrib["id"]) + ID_OFFSET)
        if node.tag.endswith("component"):
            node.attrib["objectid"] = str(
                int(node.attrib["objectid"]) + ID_OFFSET
            )
        if node.tag.endswith("item"):
            node.attrib["objectid"] = str(
                int(node.attrib["objectid"]) + ID_OFFSET
            )
        for key in list(node.attrib):
            if key.endswith("UUID") or key == "uuid":
                node.attrib[key] = str(uuid.uuid4())


def shift_settings_object(node: ET.Element) -> None:
    node.attrib["id"] = str(int(node.attrib["id"]) + ID_OFFSET)
    for part in node.findall("part"):
        part.attrib["id"] = str(int(part.attrib["id"]) + ID_OFFSET)
        part.attrib["uuid"] = str(uuid.uuid4())


def create_project(chassis: Path, drawers: Path, output: Path) -> None:
    with ZipFile(chassis) as archive:
        entries = {name: archive.read(name) for name in archive.namelist()}
    with ZipFile(drawers) as archive:
        drawer_entries = {
            name: archive.read(name) for name in archive.namelist()
        }

    main = ET.fromstring(entries["3D/3dmodel.model"])
    drawer_main = ET.fromstring(drawer_entries["3D/3dmodel.model"])
    drawer_settings = ET.fromstring(
        drawer_entries["Metadata/model_settings.config"]
    )
    shift_ids(drawer_main)

    drawer_names = {}
    for node in drawer_settings.findall("object"):
        shift_settings_object(node)
        drawer_names[node.attrib["id"]] = metadata(
            node, "name"
        ).attrib["value"]

    drawer_resources = drawer_main.find(f"{{{CORE}}}resources")
    drawer_build = drawer_main.find(f"{{{CORE}}}build")
    resources = main.find(f"{{{CORE}}}resources")
    build = main.find(f"{{{CORE}}}build")
    if any(
        node is None
        for node in [drawer_resources, drawer_build, resources, build]
    ):
        raise ValueError("Invalid 3MF model")

    for component in drawer_main.findall(
        f".//{{{CORE}}}component"
    ):
        old_path = component.attrib[f"{{{PROD}}}path"].lstrip("/")
        component.attrib[f"{{{PROD}}}path"] = f"/{PATHS[old_path]}"

    for node in list(drawer_resources):
        resources.append(node)
    for item in list(drawer_build):
        name = drawer_names[item.attrib["objectid"]]
        item.attrib["transform"] = DRAWER_TRANSFORMS[name]
        build.append(item)
    chassis_item = next(iter(build))
    chassis_item.attrib["transform"] = CHASSIS_TRANSFORM

    entries["3D/3dmodel.model"] = encoded(main)

    settings = ET.fromstring(entries["Metadata/model_settings.config"])
    chassis_plate = settings.find("plate")
    if chassis_plate is None:
        raise ValueError("Chassis project has no plate")
    for key in [
        "gcode_file",
        "thumbnail_file",
        "thumbnail_no_light_file",
        "top_file",
        "pick_file",
    ]:
        found = chassis_plate.find(f"./metadata[@key='{key}']")
        if found is not None:
            chassis_plate.remove(found)

    identify_ids = {}
    source_plate = drawer_settings.find("plate")
    if source_plate is None:
        raise ValueError("Drawer project has no plate")
    for instance in source_plate.findall("model_instance"):
        object_id = str(
            int(metadata(instance, "object_id").attrib["value"])
            + ID_OFFSET
        )
        identify_ids[object_id] = metadata(
            instance, "identify_id"
        ).attrib["value"]

    assemble = settings.find("assemble")
    insert_at = (
        list(settings).index(assemble)
        if assemble is not None
        else len(settings)
    )
    for node in drawer_settings.findall("object"):
        settings.insert(insert_at, node)
        insert_at += 1
        instance = ET.SubElement(chassis_plate, "model_instance")
        ET.SubElement(
            instance,
            "metadata",
            key="object_id",
            value=node.attrib["id"],
        )
        ET.SubElement(
            instance, "metadata", key="instance_id", value="0"
        )
        ET.SubElement(
            instance,
            "metadata",
            key="identify_id",
            value=identify_ids[node.attrib["id"]],
        )
    entries["Metadata/model_settings.config"] = encoded(settings)

    for old_path, new_path in PATHS.items():
        object_model = ET.fromstring(drawer_entries[old_path])
        shift_ids(object_model)
        entries[new_path] = encoded(object_model)

    relationships = ET.fromstring(
        entries["3D/_rels/3dmodel.model.rels"]
    )
    for index, new_path in enumerate(PATHS.values(), start=2):
        ET.SubElement(
            relationships,
            f"{{{REL}}}Relationship",
            Target=f"/{new_path}",
            Id=f"rel-{index}",
            Type=(
                "http://schemas.microsoft.com/3dmanufacturing/"
                "2013/01/3dmodel"
            ),
        )
    entries["3D/_rels/3dmodel.model.rels"] = encoded_relationships(
        relationships
    )

    entries["Metadata/slice_info.config"] = (
        b'<?xml version="1.0" encoding="UTF-8"?>\n'
        b"<config><header>"
        b'<header_item key="X-BBL-Client-Type" value="slicer"/>'
        b'<header_item key="X-BBL-Client-Version" value="02.08.02.61"/>'
        b"</header></config>\n"
    )
    entries["Metadata/filament_sequence.json"] = (
        b'{"plate_1":[1]}'
    )
    entries.pop("Metadata/_rels/model_settings.config.rels", None)
    for name in list(entries):
        if re.fullmatch(r"Metadata/plate_\d+\.gcode(?:\.md5)?", name):
            del entries[name]
        elif re.fullmatch(
            r"Metadata/(?:plate|plate_no_light|top|pick)_\d+"
            r"(?:_small)?\.(?:png|json)",
            name,
        ):
            del entries[name]

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
    print(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("chassis_project", type=Path)
    parser.add_argument("drawer_project", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    create_project(
        args.chassis_project,
        args.drawer_project,
        args.output,
    )


if __name__ == "__main__":
    main()
