"""Tests for pdf_vlm_renderer.render."""
import base64
from pathlib import Path

from PIL import Image

from pdf_vlm_renderer import (
    BoundingBox,
    crop_region,
    draw_debug_boxes,
    encode_image_base64,
    pdf_to_page_pngs,
    preprocess_for_vlm,
)


def test_pdf_to_page_pngs(tiny_pdf: Path, tmp_path: Path):
    out_dir = tmp_path / "pngs"
    out_dir.mkdir()
    pngs = pdf_to_page_pngs(tiny_pdf, out_dir, dpi=72)
    assert len(pngs) == 2
    for png in pngs:
        assert png.exists()
        img = Image.open(png)
        assert img.size[0] > 0


def test_encode_image_base64(tiny_pdf: Path, tmp_path: Path):
    pngs = pdf_to_page_pngs(tiny_pdf, tmp_path, dpi=72)
    b64 = encode_image_base64(pngs[0])
    base64.b64decode(b64)


def test_crop_region(tiny_pdf: Path, tmp_path: Path):
    pngs = pdf_to_page_pngs(tiny_pdf, tmp_path, dpi=72)
    img = Image.open(pngs[0])
    w, h = img.size
    box = BoundingBox(x_min=0, y_min=0, x_max=w // 2, y_max=h // 2)
    cropped = crop_region(pngs[0], box, tmp_path / "cropped.png", pad_px=5)
    assert cropped is not None
    assert cropped.exists()
    cropped_img = Image.open(cropped)
    assert cropped_img.size[0] <= w // 2 + 10


def test_preprocess_for_vlm(tiny_pdf: Path, tmp_path: Path):
    pngs = pdf_to_page_pngs(tiny_pdf, tmp_path, dpi=72)
    out = preprocess_for_vlm(pngs[0], tmp_path / "preprocessed.png")
    assert out.exists()


def test_draw_debug_boxes(tiny_pdf: Path, tmp_path: Path):
    pngs = pdf_to_page_pngs(tiny_pdf, tmp_path, dpi=72)
    boxes = [BoundingBox(x_min=10, y_min=10, x_max=50, y_max=50, label="Front")]
    out = tmp_path / "overlay.png"
    draw_debug_boxes(pngs[0], boxes, out)
    assert out.exists()


def test_bounding_box_dimensions():
    b = BoundingBox(x_min=0, y_min=0, x_max=100, y_max=50)
    assert b.width == 100
    assert b.height == 50
