"""Command line interface for the image cropping utility."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

from .processor import ImageProcessingError, process_image


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Crop images and optionally apply rounded corners before exporting to "
            "PNG or JPEG."
        )
    )
    parser.add_argument("input", type=Path, help="Path to the source image.")
    parser.add_argument("output", type=Path, help="Destination path for the processed image.")

    parser.add_argument("--left", type=int, default=None, help="Left coordinate of the crop area.")
    parser.add_argument("--top", type=int, default=None, help="Top coordinate of the crop area.")
    parser.add_argument(
        "--right",
        type=int,
        default=None,
        help="Right coordinate of the crop area (exclusive).",
    )
    parser.add_argument(
        "--bottom",
        type=int,
        default=None,
        help="Bottom coordinate of the crop area (exclusive).",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=None,
        help="Width of the crop area, used together with --left.",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=None,
        help="Height of the crop area, used together with --top.",
    )
    parser.add_argument(
        "--corner-radius",
        type=int,
        default=0,
        help="Corner radius in pixels. Set to 0 for square corners.",
    )
    parser.add_argument(
        "--output-format",
        choices=["png", "jpg", "jpeg"],
        default=None,
        help="Explicitly set the output format instead of inferring from the file extension.",
    )
    parser.add_argument(
        "--background-color",
        default="#FFFFFF",
        help=(
            "Background colour used when exporting to JPEG and rounded corners are requested. "
            "Accepts values in #RRGGBB format."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not args.input.exists():
        parser.error(f"Input file '{args.input}' does not exist.")

    # Ensure we can open the image before continuing to provide an early, friendly error.
    try:
        with Image.open(args.input):
            pass
    except OSError as exc:  # pragma: no cover - depends on Pillow error message
        parser.error(f"Failed to open '{args.input}': {exc}")

    try:
        process_image(
            args.input,
            args.output,
            left=args.left,
            top=args.top,
            right=args.right,
            bottom=args.bottom,
            width=args.width,
            height=args.height,
            corner_radius=args.corner_radius,
            output_format=args.output_format,
            background_color=args.background_color,
        )
    except ImageProcessingError as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
