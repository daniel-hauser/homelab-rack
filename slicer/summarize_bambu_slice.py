"""Generate release estimate data from native Bambu Studio G-code."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from zipfile import ZipFile


TIME = re.compile(
    r"; model printing time: ([^;]+); total estimated time: ([^\r\n]+)"
)


def seconds(value: str) -> int:
    units = {"d": 86400, "h": 3600, "m": 60, "s": 1}
    return sum(
        int(number) * units[unit]
        for number, unit in re.findall(r"(\d+)([dhms])", value)
    )


def metric(text: str, label: str) -> float:
    match = re.search(rf"^; {re.escape(label)} : ([0-9.]+)$", text, re.M)
    if match is None:
        raise ValueError(f"Missing G-code metric: {label}")
    return float(match.group(1))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("production_dir", type=Path)
    parser.add_argument("project", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    result = json.loads(
        (args.production_dir / "result.json").read_text(encoding="utf-8")
    )
    if result.get("return_code") != 0:
        raise ValueError(result.get("error_string", "Bambu slicing failed"))
    warnings = {
        int(item["id"]): item.get("warning_message", "")
        for item in result["sliced_plates"]
    }

    plates = []
    with ZipFile(args.project) as archive:
        project_settings = json.loads(
            archive.read("Metadata/project_settings.config")
        )
        for index, gcode in enumerate(
            sorted(args.production_dir.glob("plate_*.gcode")), start=1
        ):
            text = gcode.read_text(encoding="utf-8", errors="ignore")
            times = TIME.search(text)
            if times is None:
                raise ValueError(f"Missing print-time header in {gcode}")
            plate = json.loads(
                archive.read(f"Metadata/plate_{index}.json")
            )
            total_time = times.group(2).strip()
            plates.append(
                {
                    "plate": f"plate_{index}",
                    "objects": [
                        item["name"] for item in plate["bbox_objects"]
                    ],
                    "model_time": times.group(1).strip(),
                    "total_time": total_time,
                    "seconds": seconds(total_time),
                    "g": round(
                        metric(text, "total filament weight [g]"), 2
                    ),
                    "m": metric(text, "total filament length [mm]") / 1000,
                    "cm3": metric(
                        text, "total filament volume [cm^3]"
                    )
                    / 1000,
                    "warning_message": warnings.get(index, ""),
                }
            )

    totals = {
        "beds": len(plates),
        "grams": round(sum(item["g"] for item in plates), 2),
        "length_m": sum(item["m"] for item in plates),
        "volume_cm3": sum(item["cm3"] for item in plates),
        "serial_seconds": sum(item["seconds"] for item in plates),
    }
    total_seconds = totals["serial_seconds"]
    totals["serial_time"] = (
        f"{total_seconds // 3600}h"
        f"{total_seconds % 3600 // 60:02d}m"
        f"{total_seconds % 60:02d}s"
    )
    support_label = (
        "manual targeted normal supports / supports may start on model"
        if project_settings.get("enable_support") == "1"
        else "no support"
    )
    report = {
        "profile": (
            "Bambu Studio 02.08.02.61 / A1 0.4 / 0.20 Standard / "
            "existing pinned filament profile / 4 walls / 5 top / "
            f"4 bottom / 20% gyroid / {support_label} / no brim or skirt"
        ),
        "plates": plates,
        "totals": totals,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
