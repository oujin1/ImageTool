"""Core image processing helpers used by the command line interface."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Tuple

from PIL import Image, ImageDraw


@dataclass(frozen=True)
class CropConfig:
    """Normalized configuration for the cropping rectangle."""

    left: int
    top: int
    right: int
    bottom: int

    @property
    def box(self) -> Tuple[int, int, int, int]:
        """Return the tuple representation expected by :mod:`PIL.Image`."""

        return (self.left, self.top, self.right, self.bottom)


class ImageProcessingError(RuntimeError):
    """Raised when the provided arguments cannot be satisfied."""


def _normalise_dimension(value: int | None, fallback: int) -> int:
    return fallback if value is None else int(value)


def _resolve_crop_config(
    *,
    left: int | None,
    top: int | None,
    right: int | None,
    bottom: int | None,
    width: int | None,
    height: int | None,
    image_size: Tuple[int, int],
) -> CropConfig:
    """Validate and convert user supplied crop values to a :class:`CropConfig`.

    The function allows specifying either ``right``/``bottom`` or ``width``/``height``.
    ``left`` and ``top`` default to zero when not provided. ``right`` and ``bottom``
    default to the image's size when not provided.
    """

    img_width, img_height = image_size
    left = _normalise_dimension(left, 0)
    top = _normalise_dimension(top, 0)

    if right is None and width is not None:
        right = left + int(width)
    right = _normalise_dimension(right, img_width)

    if bottom is None and height is not None:
        bottom = top + int(height)
    bottom = _normalise_dimension(bottom, img_height)

    if left < 0 or top < 0:
        raise ImageProcessingError("Crop origin cannot be negative.")
    if right > img_width or bottom > img_height:
        raise ImageProcessingError("Crop rectangle extends beyond the image bounds.")
    if right <= left or bottom <= top:
        raise ImageProcessingError("Crop rectangle must have positive width and height.")

    return CropConfig(left=left, top=top, right=right, bottom=bottom)


def crop_image(image: Image.Image, crop: CropConfig) -> Image.Image:
    """Return a cropped copy of ``image`` using the given configuration."""

    return image.crop(crop.box)


def apply_rounded_corners(image: Image.Image, radius: int) -> Image.Image:
    """Apply rounded corners to ``image`` and return the resulting image."""

    if radius <= 0:
        return image.copy()

    width, height = image.size
    max_radius = min(width, height) // 2
    radius = min(radius, max_radius)

    if radius == 0:
        return image.copy()

    image_with_alpha = image.convert("RGBA")

    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, width, height), radius=radius, fill=255)

    image_with_alpha.putalpha(mask)
    return image_with_alpha


def _normalise_format(output: str | None, output_path: Path) -> str:
    """Determine the desired image format from CLI arguments and file name."""

    if output is not None:
        fmt = output.strip().upper()
    else:
        suffix = output_path.suffix.lower()
        fmt = {
            ".jpg": "JPEG",
            ".jpeg": "JPEG",
            ".png": "PNG",
        }.get(suffix)
        if fmt is None:
            raise ImageProcessingError(
                "Unable to infer output format from file extension. Use --output-format."
            )
    if fmt == "JPG":
        fmt = "JPEG"
    if fmt not in {"PNG", "JPEG"}:
        raise ImageProcessingError("Only PNG and JPEG formats are supported.")
    return fmt


def _parse_background_color(color: str | Iterable[int]) -> Tuple[int, int, int]:
    if isinstance(color, str):
        value = color.strip()
        if value.startswith("#"):
            value = value[1:]
        if len(value) != 6:
            raise ImageProcessingError("Background colour must be in #RRGGBB format.")
        try:
            r = int(value[0:2], 16)
            g = int(value[2:4], 16)
            b = int(value[4:6], 16)
        except ValueError as exc:  # pragma: no cover - defensive
            raise ImageProcessingError("Background colour contains invalid characters.") from exc
        return (r, g, b)

    values = tuple(int(component) for component in color)
    if len(values) != 3:
        raise ImageProcessingError("Background colour must contain three values.")
    if any(component < 0 or component > 255 for component in values):
        raise ImageProcessingError("Background colour components must be between 0 and 255.")
    return values


def save_image(
    image: Image.Image,
    output_path: Path,
    *,
    output_format: str,
    background_color: Tuple[int, int, int] = (255, 255, 255),
) -> None:
    """Save ``image`` to ``output_path`` honouring JPEG transparency limitations."""

    if output_format == "PNG":
        image.save(output_path, format=output_format)
        return

    # For JPEG we need to composite over a solid background colour.
    if image.mode in {"RGBA", "LA"} or ("transparency" in image.info):
        rgb_image = Image.new("RGB", image.size, background_color)
        alpha = image.split()[-1] if image.mode in {"RGBA", "LA"} else None
        rgb_image.paste(image, mask=alpha)
    else:
        rgb_image = image.convert("RGB")
    rgb_image.save(output_path, format=output_format)


def process_image(
    input_path: Path | str,
    output_path: Path | str,
    *,
    left: int | None = None,
    top: int | None = None,
    right: int | None = None,
    bottom: int | None = None,
    width: int | None = None,
    height: int | None = None,
    corner_radius: int = 0,
    output_format: str | None = None,
    background_color: str | Iterable[int] = (255, 255, 255),
) -> Path:
    """High level convenience wrapper used by the command line interface."""

    input_path = Path(input_path)
    output_path = Path(output_path)

    with Image.open(input_path) as source_image:
        crop = _resolve_crop_config(
            left=left,
            top=top,
            right=right,
            bottom=bottom,
            width=width,
            height=height,
            image_size=source_image.size,
        )
        cropped = crop_image(source_image, crop)

    processed = apply_rounded_corners(cropped, corner_radius)

    fmt = _normalise_format(output_format, output_path)
    background = _parse_background_color(background_color)
    save_image(processed, output_path, output_format=fmt, background_color=background)
    return output_path
