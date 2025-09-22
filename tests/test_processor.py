from pathlib import Path

import pytest
from PIL import Image

from imagetool.processor import (
    CropConfig,
    ImageProcessingError,
    apply_rounded_corners,
    crop_image,
    process_image,
    save_image,
)


@pytest.fixture()
def sample_image(tmp_path: Path) -> Path:
    path = tmp_path / "sample.png"
    image = Image.new("RGB", (100, 100), color=(255, 0, 0))
    image.save(path)
    return path


def test_crop_image_returns_expected_size(sample_image: Path):
    with Image.open(sample_image) as img:
        config = CropConfig(left=10, top=10, right=60, bottom=80)
        result = crop_image(img, config)
    assert result.size == (50, 70)


def test_apply_rounded_corners_creates_transparent_corners(sample_image: Path):
    with Image.open(sample_image) as img:
        cropped = img.crop((0, 0, 20, 20))
    rounded = apply_rounded_corners(cropped, radius=6)
    assert rounded.mode == "RGBA"
    top_left_pixel = rounded.getpixel((0, 0))
    assert top_left_pixel[3] == 0


def test_process_image_end_to_end(tmp_path: Path, sample_image: Path):
    output = tmp_path / "output.png"
    process_image(
        sample_image,
        output,
        left=10,
        top=10,
        width=50,
        height=40,
        corner_radius=8,
    )

    assert output.exists()
    with Image.open(output) as processed:
        assert processed.size == (50, 40)
        assert processed.mode == "RGBA"


def test_save_image_converts_to_jpeg_without_alpha(tmp_path: Path):
    image = Image.new("RGBA", (20, 20), (255, 0, 0, 0))
    output = tmp_path / "out.jpg"
    save_image(image, output, output_format="JPEG", background_color=(255, 255, 255))

    with Image.open(output) as saved:
        assert saved.mode == "RGB"


def test_invalid_crop_configuration_raises(sample_image: Path):
    with pytest.raises(ImageProcessingError):
        process_image(sample_image, sample_image.with_name("out.png"), left=-1)
