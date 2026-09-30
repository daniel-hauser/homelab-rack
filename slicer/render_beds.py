"""Render exact first-layer toolpaths for every sliced production plate."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from zipfile import ZipFile

from PIL import Image, ImageDraw, ImageFont


BED_MM = 256
CANVAS = 1100
MARGIN = 95
BED_PX = 900
SCALE = BED_PX / BED_MM
PALETTE = [
    "#43A6DD",
    "#F2754E",
    "#75C66A",
    "#E3B341",
    "#A882E3",
    "#56C8B4",
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    names = (
        ["DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf", "Arial Bold.ttf", "seguisb.ttf"]
        if bold
        else ["DejaVuSans.ttf", "LiberationSans-Regular.ttf", "Arial.ttf", "segoeui.ttf"]
    )
    font_dirs = [
        Path(__file__).parent / "fonts",
        Path(r"C:\Windows\Fonts"),
        Path("/usr/share/fonts/truetype/dejavu"),
        Path("/usr/share/fonts/truetype/liberation2"),
        Path("/Library/Fonts"),
        Path.home() / "Library/Fonts",
    ]
    for name in names:
        for directory in font_dirs:
            candidate = directory / name
            if candidate.is_file():
                return ImageFont.truetype(str(candidate), size)
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


def xy(point: tuple[float, float]) -> tuple[float, float]:
    x, y = point
    return MARGIN + x * SCALE, MARGIN + (BED_MM - y) * SCALE


def plate_paths(gcode: Path) -> dict[str, list[tuple[tuple[float, float], tuple[float, float]]]]:
    paths: dict[str, list[tuple[tuple[float, float], tuple[float, float]]]] = {}
    current_object = "model"
    current_xy: tuple[float, float] | None = None
    in_first_layer = False
    seen_first_layer = False

    for line in gcode.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith("; layer num/total_layer_count: 1/"):
            in_first_layer = True
            seen_first_layer = True
            continue
        if seen_first_layer and in_first_layer and line == "; CHANGE_LAYER":
            break
        if not in_first_layer:
            continue

        object_match = re.match(r"; printing object (.+?) id:", line)
        if object_match:
            current_object = object_match.group(1)
            continue
        if not line.startswith(("G0 ", "G1 ")):
            continue

        values = {
            key: float(value)
            for key, value in re.findall(
                r"([XYE])(-?\d+(?:\.\d+)?)",
                line,
            )
        }
        if "X" not in values and "Y" not in values:
            continue
        old_xy = current_xy
        current_xy = (
            values.get("X", current_xy[0] if current_xy else 0.0),
            values.get("Y", current_xy[1] if current_xy else 0.0),
        )
        if (
            old_xy is not None
            and values.get("E", 0.0) > 0
            and all(0 <= value <= BED_MM for value in (*old_xy, *current_xy))
        ):
            paths.setdefault(current_object, []).append((old_xy, current_xy))
    return paths


def render_plate(
    index: int,
    plate: dict,
    metrics: dict,
    paths: dict[str, list[tuple[tuple[float, float], tuple[float, float]]]],
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
        width = 2 if mm % 50 == 0 else 1
        x0, y0 = xy((mm, 0))
        x1, y1 = xy((mm, BED_MM))
        draw.line([x0, y0, x1, y1], fill=color, width=width)
        x0, y0 = xy((0, mm))
        x1, y1 = xy((BED_MM, mm))
        draw.line([x0, y0, x1, y1], fill=color, width=width)

    colors: dict[str, str] = {}
    for color_index, (name, segments) in enumerate(paths.items()):
        color = PALETTE[color_index % len(PALETTE)]
        colors[name] = color
        for start, end in segments:
            draw.line([xy(start), xy(end)], fill=color, width=2)

    for item in plate["bbox_objects"]:
        x0, y0, x1, y1 = item["bbox"]
        center = xy(((x0 + x1) / 2, (y0 + y1) / 2))
        label = item["name"].removesuffix(".stl").replace("_", " ")
        label_font = font(18, bold=True)
        box = draw.textbbox((0, 0), label, font=label_font)
        pad = 7
        draw.rounded_rectangle(
            [
                center[0] - (box[2] - box[0]) / 2 - pad,
                center[1] - (box[3] - box[1]) / 2 - pad,
                center[0] + (box[2] - box[0]) / 2 + pad,
                center[1] + (box[3] - box[1]) / 2 + pad,
            ],
            radius=6,
            fill="#11161DDD",
            outline=colors.get(item["name"], "#B9C2CE"),
            width=2,
        )
        draw.text(
            center,
            label,
            font=label_font,
            fill="#FFFFFF",
            anchor="mm",
        )

    draw.text(
        (MARGIN, 34),
        f"A1 BUILD PLATE {index}",
        font=font(30, bold=True),
        fill="#111827",
    )
    draw.text(
        (MARGIN + BED_PX, 37),
        f"{metrics['g']:.2f} g  |  {metrics['total_time']}",
        font=font(22),
        fill="#374151",
        anchor="ra",
    )
    draw.text(
        (MARGIN, MARGIN + BED_PX + 34),
        "256 x 256 mm | first-layer sliced toolpaths | 0.20 mm, 4 walls, 20% gyroid",
        font=font(18),
        fill="#4B5563",
    )
    image.save(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("production_dir", type=Path)
    parser.add_argument("sliced_3mf", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    estimate = json.loads(
        (args.production_dir / "estimate.json").read_text(encoding="utf-8")
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)

    images = []
    with ZipFile(args.sliced_3mf) as archive:
        for index, metrics in enumerate(estimate["plates"], start=1):
            plate = json.loads(
                archive.read(f"Metadata/plate_{index}.json")
            )
            output = args.output_dir / f"bed_{index}.png"
            render_plate(
                index,
                plate,
                metrics,
                plate_paths(args.production_dir / f"plate_{index}.gcode"),
                output,
            )
            images.append(Image.open(output))
            print(output)

    sheet = Image.new("RGB", (CANVAS * 2, CANVAS * 3), "#E5E7EB")
    positions = [
        (0, 0),
        (CANVAS, 0),
        (0, CANVAS),
        (CANVAS, CANVAS),
        (0, CANVAS * 2),
        (CANVAS, CANVAS * 2),
    ]
    for image, position in zip(images, positions):
        sheet.paste(image, position)
    sheet.save(args.output_dir / "all_beds.png")
    print(args.output_dir / "all_beds.png")


if __name__ == "__main__":
    main()
