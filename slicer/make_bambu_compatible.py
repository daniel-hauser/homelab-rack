"""Convert OrcaSlicer percentage line widths to Bambu Studio millimetres."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


LINE_WIDTHS_MM = {
    "skeleton_infill_line_width": "0.48",
    "skin_infill_line_width": "0.45",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    temp = args.output.with_suffix(args.output.suffix + ".tmp")
    with ZipFile(args.source) as source, ZipFile(
        temp,
        "w",
        compression=ZIP_DEFLATED,
        compresslevel=9,
    ) as output:
        for item in source.infolist():
            data = source.read(item.filename)
            if item.filename == "Metadata/project_settings.config":
                settings = json.loads(data)
                for key, value in LINE_WIDTHS_MM.items():
                    settings[key] = value
                data = json.dumps(settings, indent=4).encode("utf-8")
            output.writestr(item, data)

    temp.replace(args.output)
    print(args.output)


if __name__ == "__main__":
    main()
