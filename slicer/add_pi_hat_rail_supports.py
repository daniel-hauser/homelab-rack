"""Add two removable manual enforcers beneath the raised Pi-bay front rails."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import json
import re
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from add_targeted_supports import CORE, PROD, box_mesh, encoded


TARGET = "04_Dual_Pi_Chassis_5mm_HAT_Clearance.stl"
ENFORCERS = [
    (25.0, 0.0, 6.2, 84.0, 8.0, 43.5),
    (157.0, 0.0, 6.2, 216.0, 8.0, 43.5),
]


def add_supports(source: Path, output: Path) -> None:
    with ZipFile(source) as archive:
        entries = {name: archive.read(name) for name in archive.namelist()}

    settings = ET.fromstring(entries["Metadata/model_settings.config"])
    main = ET.fromstring(entries["3D/3dmodel.model"])
    resources = main.find(f"{{{CORE}}}resources")
    if resources is None:
        raise ValueError("Project has no 3MF resources")

    settings_object = next(
        (
            node
            for node in settings.findall("object")
            if node.find("./metadata[@key='name']").attrib["value"] == TARGET
        ),
        None,
    )
    if settings_object is None:
        raise ValueError(f"Missing replacement chassis: {TARGET}")
    object_id = settings_object.attrib["id"]
    main_object = resources.find(f"./{{{CORE}}}object[@id='{object_id}']")
    if main_object is None:
        raise ValueError(f"Missing main 3MF object: {object_id}")
    components = main_object.find(f"{{{CORE}}}components")
    if components is None or len(components) != 1:
        raise ValueError("Unexpected replacement component layout")
    model_path = components[0].attrib[f"{{{PROD}}}path"].lstrip("/")

    object_model = ET.fromstring(entries[model_path])
    object_resources = object_model.find(f"{{{CORE}}}resources")
    if object_resources is None:
        raise ValueError(f"Missing object resources in {model_path}")
    part_ids = [
        int(part.attrib["id"])
        for node in settings.findall("object")
        for part in node.findall("part")
    ]
    next_part_id = max(part_ids) + 2

    for index, bounds in enumerate(ENFORCERS, start=1):
        enforcer_id = next_part_id
        next_part_id += 2
        enforcer_uuid = str(uuid.uuid4())
        mesh_object = ET.SubElement(
            object_resources,
            f"{{{CORE}}}object",
            {
                "id": str(enforcer_id),
                f"{{{PROD}}}UUID": enforcer_uuid,
                "type": "model",
            },
        )
        mesh_object.append(box_mesh(bounds))
        ET.SubElement(
            components,
            f"{{{CORE}}}component",
            {
                f"{{{PROD}}}path": f"/{model_path}",
                "objectid": str(enforcer_id),
                f"{{{PROD}}}UUID": str(uuid.uuid4()),
                "transform": "1 0 0 0 1 0 0 0 1 0 0 0",
            },
        )
        part = ET.SubElement(
            settings_object,
            "part",
            {
                "id": str(enforcer_id),
                "subtype": "support_enforcer",
                "uuid": enforcer_uuid,
            },
        )
        ET.SubElement(
            part,
            "metadata",
            key="name",
            value=f"Pi bay {index} raised top-rail support enforcer",
        )
        ET.SubElement(
            part,
            "metadata",
            key="matrix",
            value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1",
        )
        ET.SubElement(
            part,
            "mesh_stat",
            face_count="12",
            edges_fixed="0",
            degenerate_facets="0",
            facets_removed="0",
            facets_reversed="0",
            backwards_edges="0",
        )

    entries[model_path] = encoded(object_model)
    entries["3D/3dmodel.model"] = encoded(main)
    entries["Metadata/model_settings.config"] = encoded(settings)

    project = json.loads(entries["Metadata/project_settings.config"])
    project.update(
        {
            "enable_support": "1",
            "support_type": "normal(manual)",
            "support_on_build_plate_only": "1",
            "support_critical_regions_only": "0",
            "support_style": "default",
            "support_top_z_distance": "0.2",
            "support_bottom_z_distance": "0.2",
            "support_interface_top_layers": "2",
            "support_interface_bottom_layers": "0",
        }
    )
    entries["Metadata/project_settings.config"] = json.dumps(
        project, separators=(",", ":")
    ).encode("utf-8")

    for entry in list(entries):
        if re.fullmatch(r"Metadata/plate_\d+\.gcode(?:\.md5)?", entry):
            del entries[entry]
        elif re.fullmatch(
            r"Metadata/(?:plate|plate_no_light|top|pick)_\d+"
            r"(?:_small)?\.(?:png|json)",
            entry,
        ):
            del entries[entry]
    entries.pop("Metadata/_rels/model_settings.config.rels", None)

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    with ZipFile(
        temporary, "w", compression=ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for name, data in entries.items():
            archive.writestr(name, data)
    temporary.replace(output)
    print(f"Added {len(ENFORCERS)} Pi top-rail support enforcers: {output}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    add_supports(args.source, args.output)


if __name__ == "__main__":
    main()
