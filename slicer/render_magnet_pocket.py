"""Render the replacement Pi drawer magnet-pocket section diagram."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH = 1600
HEIGHT = 1000
SCALE = 100
CENTER_X = 800
BED_Y = 860


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path(r"C:\Windows\Fonts\segoeui.ttf"),
        Path(r"C:\Windows\Fonts\arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def px_x(value: float) -> int:
    return round(CENTER_X + value * SCALE)


def px_z(value: float) -> int:
    return round(BED_Y - value * SCALE)


def arrow(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    fill: str = "#111827",
) -> None:
    draw.line([start, end], fill=fill, width=3)
    for point, direction in [(start, 1), (end, -1)]:
        x, y = point
        if start[1] == end[1]:
            draw.polygon(
                [
                    (x, y),
                    (x + direction * 12, y - 7),
                    (x + direction * 12, y + 7),
                ],
                fill=fill,
            )
        else:
            draw.polygon(
                [(x, y), (x - 7, y + direction * 12), (x + 7, y + direction * 12)],
                fill=fill,
            )


def render(output: Path) -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), "#F8FAFC")
    draw = ImageDraw.Draw(image)
    title = font(42)
    label = font(28)
    small = font(24)

    draw.text(
        (70, 45),
        "PI DRAWER 6 MM MAGNET GLUE-POCKET SECTION",
        font=title,
        fill="#111827",
    )
    draw.text(
        (70, 100),
        "Dimensions in millimetres - magnet glues against the insulating roof",
        font=small,
        fill="#475569",
    )

    boss_left = px_x(-4.3)
    boss_right = px_x(4.3)
    boss_top = px_z(6.8)
    draw.rectangle(
        [boss_left, boss_top, boss_right, BED_Y],
        fill="#94A3B8",
        outline="#334155",
        width=4,
    )

    mouth_left = px_x(-3.5)
    mouth_right = px_x(3.5)
    bore_left = px_x(-3.3)
    bore_right = px_x(3.3)
    flare_top = px_z(0.7)
    pocket_roof = px_z(4.55)
    skin_top = px_z(4.85)
    screw_left = px_x(-2.8)
    screw_right = px_x(2.8)

    draw.polygon(
        [
            (mouth_left, BED_Y + 2),
            (mouth_right, BED_Y + 2),
            (bore_right, flare_top),
            (bore_right, pocket_roof),
            (bore_left, pocket_roof),
            (bore_left, flare_top),
        ],
        fill="#FFFFFF",
        outline="#0F172A",
    )
    draw.rectangle(
        [screw_left, boss_top - 2, screw_right, skin_top],
        fill="#FFFFFF",
        outline="#0F172A",
        width=2,
    )
    draw.rectangle(
        [bore_left, skin_top, bore_right, pocket_roof],
        fill="#FACC15",
        outline="#A16207",
        width=2,
    )

    magnet_top = pocket_roof
    magnet_bottom = px_z(2.55)
    draw.rectangle(
        [px_x(-3), magnet_top, px_x(3), magnet_bottom],
        fill="#DC2626",
        outline="#7F1D1D",
        width=3,
    )
    draw.text(
        (CENTER_X - 82, magnet_top + 65),
        "MAGNET",
        font=small,
        fill="#FFFFFF",
    )

    arrow(draw, (mouth_left, 920), (mouth_right, 920))
    draw.text(
        (CENTER_X - 95, 930),
        "7.00 mouth",
        font=label,
        fill="#111827",
    )

    arrow(draw, (bore_left, 350), (bore_right, 350))
    draw.text(
        (CENTER_X - 92, 305),
        "6.60 bore",
        font=label,
        fill="#111827",
    )

    arrow(draw, (boss_left, 215), (boss_right, 215))
    draw.text(
        (CENTER_X - 108, 165),
        "8.60 boss OD",
        font=label,
        fill="#111827",
    )

    arrow(draw, (1290, BED_Y), (1290, flare_top))
    draw.text((1320, 785), "0.70 entrance flare", font=label, fill="#111827")

    arrow(draw, (1290, skin_top), (1290, pocket_roof))
    draw.text((1320, 375), "0.30 insulating skin", font=label, fill="#111827")

    arrow(draw, (310, magnet_top), (310, magnet_bottom))
    draw.text((70, 485), "6 x 2 magnet", font=label, fill="#111827")
    draw.text((70, 525), "GLUE - DO NOT PRESS-FIT", font=small, fill="#B91C1C")

    draw.line(
        [(boss_left, 275), (bore_left, 275)],
        fill="#111827",
        width=3,
    )
    draw.text((205, 245), "1.00 radial wall", font=label, fill="#111827")
    draw.line([(465, 270), (boss_left, 275)], fill="#111827", width=2)

    draw.line([(0, BED_Y), (WIDTH, BED_Y)], fill="#64748B", width=4)
    draw.text(
        (70, 875),
        "PRINT BED / UNDERSIDE ENTRY",
        font=small,
        fill="#475569",
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)
    print(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    render(args.output)


if __name__ == "__main__":
    main()
