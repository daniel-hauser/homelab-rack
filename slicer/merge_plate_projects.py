"""Merge a one-plate test 3MF before a multi-plate production 3MF."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import json
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
PROD = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
PLATE_COLUMNS = 3
PLATE_PITCH = 307.2
ET.register_namespace("", CORE)
ET.register_namespace("p", PROD)


def xml(data: bytes) -> ET.Element:
    return ET.fromstring(data)


def encoded(root: ET.Element) -> bytes:
    ET.indent(root, space=" ")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def encoded_relationships(root: ET.Element) -> bytes:
    ET.register_namespace("", REL)
    try:
        return encoded(root)
    finally:
        ET.register_namespace("", CORE)


def replace_uuids(root: ET.Element) -> None:
    for node in root.iter():
        for key in list(node.attrib):
            if key.endswith("UUID"):
                node.attrib[key] = str(uuid.uuid4())


def shift_main_model(root: ET.Element, offset: int) -> None:
    for node in root.findall(f".//{{{CORE}}}object"):
        node.attrib["id"] = str(int(node.attrib["id"]) + offset)
    for node in root.findall(f".//{{{CORE}}}component"):
        node.attrib["objectid"] = str(
            int(node.attrib["objectid"]) + offset
        )
    for node in root.findall(f".//{{{CORE}}}item"):
        node.attrib["objectid"] = str(
            int(node.attrib["objectid"]) + offset
        )
    replace_uuids(root)


def plate_origin(index: int) -> tuple[float, float]:
    zero_based = index - 1
    return (
        (zero_based % PLATE_COLUMNS) * PLATE_PITCH,
        -(zero_based // PLATE_COLUMNS) * PLATE_PITCH,
    )


def shift_build_plates(
    main_root: ET.Element,
    settings_root: ET.Element,
    object_offset: int,
    plate_offset: int,
) -> None:
    object_plates: dict[int, int] = {}
    for plate in settings_root.findall("plate"):
        old_index = int(metadata_value(plate, "plater_id").attrib["value"])
        for instance in plate.findall("model_instance"):
            old_id = int(
                metadata_value(instance, "object_id").attrib["value"]
            )
            object_plates[old_id + object_offset] = old_index

    for item in main_root.findall(f".//{{{CORE}}}item"):
        object_id = int(item.attrib["objectid"])
        old_index = object_plates[object_id]
        old_x, old_y = plate_origin(old_index)
        new_x, new_y = plate_origin(old_index + plate_offset)
        transform = [float(value) for value in item.attrib["transform"].split()]
        transform[9] += new_x - old_x
        transform[10] += new_y - old_y
        item.attrib["transform"] = " ".join(
            f"{value:.9g}" for value in transform
        )


def shift_object_model(root: ET.Element, offset: int) -> None:
    for node in root.findall(f".//{{{CORE}}}object"):
        node.attrib["id"] = str(int(node.attrib["id"]) + offset)
    replace_uuids(root)


def metadata_value(node: ET.Element, key: str) -> ET.Element:
    for child in node.findall("metadata"):
        if child.attrib.get("key") == key:
            return child
    raise ValueError(f"Missing metadata key: {key}")


def shift_model_settings(
    root: ET.Element,
    offset: int,
    plate_offset: int,
) -> None:
    for node in root.findall("object"):
        node.attrib["id"] = str(int(node.attrib["id"]) + offset)
        for part in node.findall("part"):
            part.attrib["id"] = str(int(part.attrib["id"]) + offset)
    for plate in root.findall("plate"):
        plater = metadata_value(plate, "plater_id")
        plater.attrib["value"] = str(
            int(plater.attrib["value"]) + plate_offset
        )
        gcode = metadata_value(plate, "gcode_file")
        old = int(
            gcode.attrib["value"]
            .removeprefix("Metadata/plate_")
            .removesuffix(".gcode")
        )
        gcode.attrib["value"] = (
            f"Metadata/plate_{old + plate_offset}.gcode"
        )
        for instance in plate.findall("model_instance"):
            object_id = metadata_value(instance, "object_id")
            object_id.attrib["value"] = str(
                int(object_id.attrib["value"]) + offset
            )


def shift_slice_info(root: ET.Element, plate_offset: int) -> None:
    for plate in root.findall("plate"):
        index = metadata_value(plate, "index")
        index.attrib["value"] = str(
            int(index.attrib["value"]) + plate_offset
        )


def merge_relationships(
    test_root: ET.Element,
    production_root: ET.Element,
    *,
    plate_offset: int | None = None,
) -> ET.Element:
    existing = list(test_root)
    next_id = len(existing) + 1
    for relation in list(production_root):
        relation.attrib["Id"] = f"rel-{next_id}"
        if plate_offset is not None:
            target = relation.attrib["Target"]
            old = int(
                target.removeprefix("/Metadata/plate_")
                .removesuffix(".gcode")
            )
            relation.attrib["Target"] = (
                f"/Metadata/plate_{old + plate_offset}.gcode"
            )
        test_root.append(relation)
        next_id += 1
    return test_root


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("test_project", type=Path)
    parser.add_argument("production_project", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    with ZipFile(args.test_project) as test_zip, ZipFile(
        args.production_project
    ) as production_zip:
        test_files = {
            name: test_zip.read(name) for name in test_zip.namelist()
        }
        production_files = {
            name: production_zip.read(name)
            for name in production_zip.namelist()
        }

    test_main = xml(test_files["3D/3dmodel.model"])
    production_main = xml(production_files["3D/3dmodel.model"])
    production_settings = xml(
        production_files["Metadata/model_settings.config"]
    )
    test_ids = [
        int(node.attrib["id"])
        for node in test_main.findall(f".//{{{CORE}}}object")
    ]
    offset = max(test_ids)
    shift_main_model(production_main, offset)
    shift_build_plates(
        production_main,
        production_settings,
        offset,
        1,
    )

    test_resources = test_main.find(f"{{{CORE}}}resources")
    production_resources = production_main.find(f"{{{CORE}}}resources")
    test_build = test_main.find(f"{{{CORE}}}build")
    production_build = production_main.find(f"{{{CORE}}}build")
    assert test_resources is not None and production_resources is not None
    assert test_build is not None and production_build is not None
    for node in list(production_resources):
        test_resources.append(node)
    for node in list(production_build):
        test_build.append(node)
    test_files["3D/3dmodel.model"] = encoded(test_main)

    test_settings = xml(
        test_files["Metadata/model_settings.config"]
    )
    shift_model_settings(production_settings, offset, 1)
    test_assemble = test_settings.find("assemble")
    insert_at = (
        list(test_settings).index(test_assemble)
        if test_assemble is not None
        else len(test_settings)
    )
    for node in list(production_settings):
        if node.tag != "assemble":
            test_settings.insert(insert_at, node)
            insert_at += 1
    test_files["Metadata/model_settings.config"] = encoded(
        test_settings
    )

    test_slice = xml(test_files["Metadata/slice_info.config"])
    production_slice = xml(
        production_files["Metadata/slice_info.config"]
    )
    shift_slice_info(production_slice, 1)
    for plate in production_slice.findall("plate"):
        test_slice.append(plate)
    test_files["Metadata/slice_info.config"] = encoded(test_slice)

    test_model_rels = xml(
        test_files["3D/_rels/3dmodel.model.rels"]
    )
    production_model_rels = xml(
        production_files["3D/_rels/3dmodel.model.rels"]
    )
    test_files["3D/_rels/3dmodel.model.rels"] = encoded_relationships(
        merge_relationships(
            test_model_rels,
            production_model_rels,
        )
    )

    test_gcode_rels = xml(
        test_files["Metadata/_rels/model_settings.config.rels"]
    )
    production_gcode_rels = xml(
        production_files[
            "Metadata/_rels/model_settings.config.rels"
        ]
    )
    test_files[
        "Metadata/_rels/model_settings.config.rels"
    ] = encoded_relationships(
        merge_relationships(
            test_gcode_rels,
            production_gcode_rels,
            plate_offset=1,
        )
    )

    sequence = json.loads(
        test_files["Metadata/filament_sequence.json"]
    )
    production_sequence = json.loads(
        production_files["Metadata/filament_sequence.json"]
    )
    for key, value in production_sequence.items():
        index = int(key.removeprefix("plate_")) + 1
        sequence[f"plate_{index}"] = value
    test_files["Metadata/filament_sequence.json"] = json.dumps(
        sequence,
        separators=(",", ":"),
    ).encode("utf-8")

    for name, data in production_files.items():
        if name.startswith("3D/Objects/") and name.endswith(".model"):
            model = xml(data)
            shift_object_model(model, offset)
            if name in test_files:
                raise ValueError(f"Duplicate object path: {name}")
            test_files[name] = encoded(model)
        elif name.startswith("Metadata/plate_"):
            suffix = name.removeprefix("Metadata/plate_")
            plate_text, extension = suffix.split(".", 1)
            new_name = (
                f"Metadata/plate_{int(plate_text) + 1}.{extension}"
            )
            test_files[new_name] = data

    # Use the production process and printer settings for all plates.
    test_files["Metadata/project_settings.config"] = production_files[
        "Metadata/project_settings.config"
    ]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    temp = args.output.with_suffix(args.output.suffix + ".tmp")
    with ZipFile(
        temp,
        "w",
        compression=ZIP_DEFLATED,
        compresslevel=9,
    ) as output:
        for name, data in test_files.items():
            output.writestr(name, data)
    temp.replace(args.output)
    print(args.output)


if __name__ == "__main__":
    main()
