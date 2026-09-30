"""Replace arranged Bambu 3MF meshes with same-named STL exports."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import hashlib
import re
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree

import trimesh


def stl_index(roots: list[Path]) -> dict[str, Path]:
    indexed: dict[str, Path] = {}
    hashes: dict[str, str] = {}

    for root in roots:
        for path in root.rglob("*.stl"):
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            existing = indexed.get(path.name)
            if existing and hashes[path.name] != digest:
                raise ValueError(
                    f"Conflicting STL files named {path.name}: "
                    f"{existing} and {path}"
                )
            indexed[path.name] = path
            hashes[path.name] = digest

    return indexed


def mesh_xml(path: Path) -> tuple[str, int]:
    loaded = trimesh.load_mesh(path, process=False)
    if isinstance(loaded, trimesh.Scene):
        mesh = loaded.to_geometry()
    else:
        mesh = loaded

    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError(f"{path} did not load as a triangle mesh")

    mesh = mesh.copy()
    mesh.merge_vertices()
    mesh.remove_unreferenced_vertices()

    center = (mesh.bounds[0] + mesh.bounds[1]) / 2
    vertices = mesh.vertices - center
    vertex_lines = "\n".join(
        f'     <vertex x="{x:.9g}" y="{y:.9g}" z="{z:.9g}"/>'
        for x, y, z in vertices
    )
    triangle_lines = "\n".join(
        f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>'
        for a, b, c in mesh.faces
    )
    xml = (
        "   <mesh>\n"
        "    <vertices>\n"
        f"{vertex_lines}\n"
        "    </vertices>\n"
        "    <triangles>\n"
        f"{triangle_lines}\n"
        "    </triangles>\n"
        "   </mesh>"
    )
    return xml, len(mesh.faces)


def replace_project(
    source: Path,
    output: Path,
    stls: dict[str, Path],
) -> None:
    with zipfile.ZipFile(source) as archive:
        entries = {name: archive.read(name) for name in archive.namelist()}

    settings_name = "Metadata/model_settings.config"
    settings = ElementTree.fromstring(entries[settings_name])
    model = ElementTree.fromstring(entries["3D/3dmodel.model"])
    core_namespace = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    production_namespace = (
        "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
    )
    object_paths: dict[str, str] = {}
    for obj in model.findall(
        f".//{{{core_namespace}}}resources/"
        f"{{{core_namespace}}}object"
    ):
        component = obj.find(
            f"./{{{core_namespace}}}components/"
            f"{{{core_namespace}}}component"
        )
        if component is None:
            continue
        path = component.attrib[
            f"{{{production_namespace}}}path"
        ].lstrip("/")
        object_paths[obj.attrib["id"]] = path
    replacements: dict[str, tuple[Path, int]] = {}

    for obj in settings.findall("object"):
        name_node = obj.find("./metadata[@key='name']")
        part = obj.find("part")
        if name_node is None or part is None:
            continue

        name = name_node.attrib["value"]
        stl = stls.get(name)
        if stl is None:
            raise FileNotFoundError(f"No replacement STL found for {name}")

        model_path = object_paths[obj.attrib["id"]]
        mesh_markup, face_count = mesh_xml(stl)
        text = entries[model_path].decode("utf-8")
        text, count = re.subn(
            r"   <mesh>.*?   </mesh>",
            mesh_markup,
            text,
            count=1,
            flags=re.DOTALL,
        )
        if count != 1:
            raise ValueError(f"Could not replace mesh in {model_path}")
        entries[model_path] = text.encode("utf-8")

        replacements[name] = (stl, face_count)

    settings_text = entries[settings_name].decode("utf-8")
    settings_text = re.sub(
        r'^\s*<metadata key="gcode_file" value="[^"]*"/>\r?\n',
        "",
        settings_text,
        flags=re.MULTILINE,
    )
    entries[settings_name] = settings_text.encode("utf-8")

    for name in list(entries):
        if re.fullmatch(r"Metadata/plate_\d+\.gcode(?:\.md5)?", name):
            del entries[name]

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        dir=output.parent,
        suffix=".3mf",
        delete=False,
    ) as temporary:
        temporary_path = Path(temporary.name)

    try:
        with zipfile.ZipFile(
            temporary_path,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=6,
        ) as archive:
            for name, data in entries.items():
                archive.writestr(name, data)
        temporary_path.replace(output)
    finally:
        temporary_path.unlink(missing_ok=True)

    print(f"Updated {len(replacements)} meshes in {output}")
    for name, (path, face_count) in replacements.items():
        print(f"  {name}: {face_count} triangles <- {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("stl_roots", nargs="+", type=Path)
    args = parser.parse_args()

    replace_project(
        args.source,
        args.output,
        stl_index(args.stl_roots),
    )


if __name__ == "__main__":
    main()
