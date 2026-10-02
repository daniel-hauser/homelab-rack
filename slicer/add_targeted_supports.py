"""Add the one safe manual support enforcer selected by native A/B slicing."""

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
ET.register_namespace("", CORE)
ET.register_namespace("p", PROD)

# The UCG box occupies only its forward, seam-side top-cap cavity. The same
# location on each USW intersects the 34 mm-deep keystone clearance; the
# opposite side contains the rack ear and slots, so the USWs remain unsupported.
ENFORCERS = {
    "01_UCG_Ultra.stl": (108.0, -70.0, -20.0, 115.0, -63.0, 18.0),
}


def encoded(root: ET.Element) -> bytes:
    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def box_mesh(bounds: tuple[float, ...]) -> ET.Element:
    x0, y0, z0, x1, y1, z1 = bounds
    vertices = [
        (x0, y0, z0),
        (x1, y0, z0),
        (x1, y1, z0),
        (x0, y1, z0),
        (x0, y0, z1),
        (x1, y0, z1),
        (x1, y1, z1),
        (x0, y1, z1),
    ]
    triangles = [
        (0, 2, 1),
        (0, 3, 2),
        (4, 5, 6),
        (4, 6, 7),
        (0, 1, 5),
        (0, 5, 4),
        (1, 2, 6),
        (1, 6, 5),
        (2, 3, 7),
        (2, 7, 6),
        (3, 0, 4),
        (3, 4, 7),
    ]
    mesh = ET.Element(f"{{{CORE}}}mesh")
    vertex_root = ET.SubElement(mesh, f"{{{CORE}}}vertices")
    for x, y, z in vertices:
        ET.SubElement(
            vertex_root,
            f"{{{CORE}}}vertex",
            x=f"{x:.6g}",
            y=f"{y:.6g}",
            z=f"{z:.6g}",
        )
    triangle_root = ET.SubElement(mesh, f"{{{CORE}}}triangles")
    for first, second, third in triangles:
        ET.SubElement(
            triangle_root,
            f"{{{CORE}}}triangle",
            v1=str(first),
            v2=str(second),
            v3=str(third),
        )
    return mesh


def add_targeted_supports(source: Path, output: Path) -> None:
    with ZipFile(source) as archive:
        entries = {name: archive.read(name) for name in archive.namelist()}

    settings = ET.fromstring(entries["Metadata/model_settings.config"])
    main = ET.fromstring(entries["3D/3dmodel.model"])
    resources = main.find(f"{{{CORE}}}resources")
    if resources is None:
        raise ValueError("Project has no 3MF resources")

    names = {
        node.find("./metadata[@key='name']").attrib["value"]: node
        for node in settings.findall("object")
    }
    part_ids = [
        int(part.attrib["id"])
        for node in settings.findall("object")
        for part in node.findall("part")
    ]
    next_part_id = max(part_ids) + 2

    for name, bounds in ENFORCERS.items():
        settings_object = names.get(name)
        if settings_object is None:
            raise ValueError(f"Missing target chassis: {name}")
        object_id = settings_object.attrib["id"]
        main_object = resources.find(
            f"./{{{CORE}}}object[@id='{object_id}']"
        )
        if main_object is None:
            raise ValueError(f"Missing main 3MF object: {object_id}")
        components = main_object.find(f"{{{CORE}}}components")
        if components is None or len(components) != 1:
            raise ValueError(f"Unexpected component layout for {name}")
        model_path = components[0].attrib[f"{{{PROD}}}path"].lstrip("/")

        object_model = ET.fromstring(entries[model_path])
        object_resources = object_model.find(f"{{{CORE}}}resources")
        if object_resources is None:
            raise ValueError(f"Missing object resources in {model_path}")
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
        entries[model_path] = encoded(object_model)

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
            value="Forward seam-side top-cap support enforcer",
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

    project = json.loads(entries["Metadata/project_settings.config"])
    project.update(
        {
            "enable_support": "1",
            "support_type": "normal(manual)",
            "support_on_build_plate_only": "0",
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
    entries["3D/3dmodel.model"] = encoded(main)

    settings_text = encoded(settings).decode("utf-8")
    settings_text = re.sub(
        r'^\s*<metadata key="gcode_file" value="[^"]*"/>\r?\n',
        "",
        settings_text,
        flags=re.MULTILINE,
    )
    entries["Metadata/model_settings.config"] = settings_text.encode("utf-8")
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
    print(f"Added {len(ENFORCERS)} targeted support enforcers: {output}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    add_targeted_supports(args.source, args.output)


if __name__ == "__main__":
    main()
