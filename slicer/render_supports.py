"""Render top-down native-Bambu support toolpaths for audit evidence."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from zipfile import ZipFile

from PIL import Image, ImageDraw, ImageFont


BED_MM = 256
CANVAS = 1100
MARGIN = 95
BED_PX = 900
SCALE = BED_PX / BED_MM
NUMBER = r"-?(?:\d+(?:\.\d*)?|\.\d+)"
VALUE = re.compile(rf"([XYZE])({NUMBER})")


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    names = ["seguisb.ttf", "Arial Bold.ttf"] if bold else [
        "segoeui.ttf",
        "Arial.ttf",
    ]
    for name in names:
        path = Path(r"C:\Windows\Fonts") / name
        if path.is_file():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default(size=size)


def xy(point: tuple[float, float]) -> tuple[float, float]:
    x, y = point
    return MARGIN + x * SCALE, MARGIN + (BED_MM - y) * SCALE


def support_paths(
    path: Path,
) -> dict[str, list[tuple[tuple[float, float], tuple[float, float]]]]:
    feature = ""
    x: float | None = None
    y: float | None = None
    paths: dict[
        str, list[tuple[tuple[float, float], tuple[float, float]]]
    ] = {}
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith("; FEATURE:"):
            feature = line.split(":", 1)[1].strip()
            continue
        if not line.startswith(("G0 ", "G1 ")):
            continue
        values = {key: float(value) for key, value in VALUE.findall(line)}
        next_x = values.get("X", x)
        next_y = values.get("Y", y)
        if (
            feature.startswith("Support")
            and x is not None
            and y is not None
            and next_x is not None
            and next_y is not None
            and values.get("E", 0) > 0
            and math.hypot(next_x - x, next_y - y) > 0.01
        ):
            paths.setdefault(feature, []).append(
                ((x, y), (next_x, next_y))
            )
        x, y = next_x, next_y
    return paths


def render(
    index: int,
    plate: dict,
    paths: dict[
        str, list[tuple[tuple[float, float], tuple[float, float]]]
    ],
    output: Path,
) -> None:
    image = Image.new("RGB", (CANVAS, CANVAS), "#F4F6F8")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(
        [MARGIN - 8, MARGIN - 8, MARGIN + BED_PX + 8, MARGIN + BED_PX + 8],
        radius=18,
        fill="#171B22",
        outline="#2D3745",
        width=4,
    )
    for mm in range(0, BED_MM + 1, 10):
        color = "#3A4656" if mm % 50 == 0 else "#28323F"
        draw.line([xy((mm, 0)), xy((mm, BED_MM))], fill=color)
        draw.line([xy((0, mm)), xy((BED_MM, mm))], fill=color)
    for item in plate["bbox_objects"]:
        x0, y0, x1, y1 = item["bbox"]
        draw.rectangle(
            [xy((x0, y1)), xy((x1, y0))],
            outline="#718096",
            width=3,
        )
    colors = {
        "Support": "#4FD1C5",
        "Support transition": "#63B3ED",
        "Support interface": "#F6C85F",
    }
    for feature, segments in paths.items():
        for start, end in segments:
            draw.line(
                [xy(start), xy(end)],
                fill=colors.get(feature, "#FFFFFF"),
                width=4,
            )
    draw.text(
        (MARGIN, 34),
        f"TARGETED SUPPORT TOOLPATHS — PLATE {index}",
        font=font(28, bold=True),
        fill="#111827",
    )
    legend = "teal: support  |  blue: transition  |  yellow: interface"
    draw.text(
        (MARGIN, MARGIN + BED_PX + 34),
        legend,
        font=font(18),
        fill="#4B5563",
    )
    image.save(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("gcode_dir", type=Path)
    parser.add_argument("project", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with ZipFile(args.project) as archive:
        for index in range(1, 6):
            paths = support_paths(args.gcode_dir / f"plate_{index}.gcode")
            if not paths:
                continue
            plate = json.loads(
                archive.read(f"Metadata/plate_{index}.json")
            )
            output = args.output_dir / f"support_plate_{index}.png"
            render(index, plate, paths, output)
            print(output)


if __name__ == "__main__":
    main()
