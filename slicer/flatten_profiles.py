"""Flatten inherited Bambu Studio JSON profiles for reliable CLI slicing."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import sys
from pathlib import Path


def load_profiles(root: Path) -> dict[tuple[str, str], dict]:
    profiles: dict[tuple[str, str], dict] = {}
    for path in root.rglob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        name = data.get("name")
        profile_type = data.get("type")
        if name and profile_type in {"machine", "process", "filament"}:
            profiles[(profile_type, name)] = data
    return profiles


def flatten(
    profiles: dict[tuple[str, str], dict],
    profile_type: str,
    name: str,
    chain: tuple[str, ...] = (),
) -> dict:
    if name in chain:
        raise ValueError(f"Inheritance cycle: {' -> '.join((*chain, name))}")

    data = profiles[(profile_type, name)]
    parent_name = data.get("inherits")
    if parent_name:
        merged = flatten(profiles, profile_type, parent_name, (*chain, name))
        merged.update(data)
    else:
        merged = dict(data)

    merged.pop("inherits", None)
    merged["name"] = name
    merged["type"] = profile_type
    return merged


def main() -> None:
    if len(sys.argv) not in {4, 5}:
        raise SystemExit(
            "Usage: flatten_profiles.py PROFILE_ROOT OUTPUT_DIR "
            "'type:name,type:name,...' [OVERRIDES_JSON]"
        )

    profile_root = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    requests = sys.argv[3].split(",")
    overrides = {}
    if len(sys.argv) == 5:
        override_data = json.loads(
            Path(sys.argv[4]).read_text(encoding="utf-8")
        )
        overrides = {
            key: value
            for key, value in override_data.items()
            if key not in {"type", "name", "from", "instantiation"}
        }
    output_dir.mkdir(parents=True, exist_ok=True)
    profiles = load_profiles(profile_root)

    for request in requests:
        profile_type, name = request.split(":", 1)
        flattened = flatten(profiles, profile_type, name)
        flattened.update(overrides)
        safe_name = name.replace("/", "_").replace("\\", "_")
        output = output_dir / f"{profile_type}-{safe_name}.json"
        output.write_text(
            json.dumps(flattened, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(output)


if __name__ == "__main__":
    main()
