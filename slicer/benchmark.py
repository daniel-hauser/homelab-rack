"""Slice a rack STL with the reproducible A1 profile and report metrics."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ORCA = Path(r"C:\Program Files\OrcaSlicer\orca-slicer.exe")
PROFILES = ROOT / "slicer" / "profiles"
BENCHMARK_PROFILES = ROOT / "slicer" / "benchmark-profiles"


def parse_metrics(gcode: str) -> dict[str, str | float]:
    metrics: dict[str, str | float] = {}
    time_match = re.search(
        r"model printing time: ([^;]+); total estimated time: ([^\r\n]+)",
        gcode,
    )
    if time_match:
        metrics["model_time"] = time_match.group(1).strip()
        metrics["total_time"] = time_match.group(2).strip()

    for unit, value in re.findall(
        r"filament used \[(mm|cm3|g)\] = ([0-9.]+)",
        gcode,
    ):
        metrics[f"filament_{unit}"] = float(value)
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "stl",
        nargs="?",
        type=Path,
        default=ROOT / "out" / "ucg_left.stl",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output directory; defaults to slicer/results/<STL name>.",
    )
    args = parser.parse_args()

    stl = args.stl.resolve()
    output = (
        args.output.resolve()
        if args.output
        else ROOT / "slicer" / "results" / stl.stem
    )
    output.mkdir(parents=True, exist_ok=True)

    process = (
        BENCHMARK_PROFILES / "process-0.20mm Standard @BBL A1.json"
    )
    machine = PROFILES / "machine-Bambu Lab A1 0.4 nozzle.json"
    filament = PROFILES / "filament-Generic PLA @BBL A1.json"
    required = [ORCA, stl, process, machine, filament]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit(f"Missing required files: {', '.join(missing)}")

    command = [
        str(ORCA),
        str(stl),
        "--debug",
        "2",
        "--load-settings",
        f"{process};{machine}",
        "--load-filaments",
        str(filament),
        "--arrange",
        "1",
        "--ensure-on-bed",
        "--slice",
        "0",
        "--outputdir",
        str(output),
        "--export-3mf",
        f"{stl.stem}.gcode.3mf",
    ]
    completed = subprocess.run(
        command,
        cwd=output,
        capture_output=True,
        text=True,
        check=False,
    )
    log = completed.stdout + completed.stderr
    (output / "slice.log").write_text(log, encoding="utf-8")
    if completed.returncode:
        raise SystemExit(
            f"OrcaSlicer failed with exit {completed.returncode}; "
            f"see {output / 'slice.log'}"
        )

    gcode_path = output / "plate_1.gcode"
    metrics = parse_metrics(gcode_path.read_text(encoding="utf-8"))
    metrics.update(
        {
            "stl": str(stl),
            "slicer": "OrcaSlicer 2.4.2",
            "process": "0.20mm Standard @BBL A1, no brim/skirt",
        }
    )
    metrics_path = output / "metrics.json"
    metrics_path.write_text(
        json.dumps(metrics, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
