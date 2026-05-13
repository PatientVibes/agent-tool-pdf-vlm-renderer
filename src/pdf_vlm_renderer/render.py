"""PDF rendering and image manipulation — deterministic, no LLM calls."""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Optional

import pypdfium2 as pdfium
from PIL import Image, ImageDraw, ImageOps

from .models import BoundingBox


# ---------------------------------------------------------------------------
# PDF → PNG rendering (pypdfium2, Apache-2.0)
# ---------------------------------------------------------------------------


def pdf_to_page_pngs(
    pdf_path: Path, out_dir: Path, dpi: int = 300,
) -> list[Path]:
    """Render each page of a PDF to a PNG image at the given DPI."""
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf = pdfium.PdfDocument(str(pdf_path))

    scale = dpi / 72.0
    saved: list[Path] = []

    for i in range(len(pdf)):
        page = pdf[i]
        bitmap = page.render(scale=scale)
        pil_image = bitmap.to_pil()
        out_path = out_dir / f"{pdf_path.stem}_{i + 1}.png"
        pil_image.save(str(out_path))
        saved.append(out_path)

    pdf.close()
    return saved


# ---------------------------------------------------------------------------
# Image cropping
# ---------------------------------------------------------------------------


def _clamp_box_px(
    box: BoundingBox, w: int, h: int,
) -> tuple[int, int, int, int]:
    """Clamp pixel-space box to image bounds and normalize ordering."""
    px1 = max(0, min(box.x_min, w - 1))
    px2 = max(0, min(box.x_max, w - 1))
    py1 = max(0, min(box.y_min, h - 1))
    py2 = max(0, min(box.y_max, h - 1))
    px1, px2 = (px1, px2) if px1 <= px2 else (px2, px1)
    py1, py2 = (py1, py2) if py1 <= py2 else (py2, py1)
    return px1, py1, px2, py2


def crop_region(
    image_path: Path,
    box: BoundingBox,
    out_path: Path,
    pad_px: int = 10,
) -> Optional[Path]:
    """Crop a bounding box region from an image with optional padding."""
    im = Image.open(image_path).convert("RGBA")
    w, h = im.size

    px1, py1, px2, py2 = _clamp_box_px(box, w, h)

    px1 = max(0, px1 - pad_px)
    py1 = max(0, py1 - pad_px)
    px2 = min(w - 1, px2 + pad_px)
    py2 = min(h - 1, py2 + pad_px)

    if px2 <= px1 or py2 <= py1:
        return None

    crop = im.crop((px1, py1, px2 + 1, py2 + 1))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    crop.save(str(out_path))
    return out_path


# ---------------------------------------------------------------------------
# Debug visualization
# ---------------------------------------------------------------------------


_COLOR_MAP = {"Front": "lime", "Back": "red"}
_FALLBACK_COLORS = ["yellow", "cyan", "magenta", "orange"]


def draw_debug_boxes(
    image_path: Path,
    boxes: list[BoundingBox],
    out_path: Path,
    line_width: Optional[int] = None,
) -> None:
    """Draw labeled outlines on an image for visual QA."""
    im = Image.open(image_path).convert("RGBA")
    w, h = im.size

    if line_width is None:
        line_width = max(3, min(w, h) // 300)

    draw = ImageDraw.Draw(im)
    for i, box in enumerate(boxes):
        px1, py1, px2, py2 = _clamp_box_px(box, w, h)
        label = box.label or "?"
        color = _COLOR_MAP.get(label, _FALLBACK_COLORS[i % len(_FALLBACK_COLORS)])
        draw.rectangle([px1, py1, px2, py2], outline=color, width=line_width)
        text = f"{i + 1}:{label}"
        draw.text((px1 + 3, max(0, py1 - 14)), text, fill=color)

    im.save(str(out_path))


# ---------------------------------------------------------------------------
# Image preprocessing
# ---------------------------------------------------------------------------


def preprocess_for_vlm(image_path: Path, out_path: Path) -> Path:
    """Apply preprocessing to improve VLM accuracy on degraded scans.

    Normalizes contrast and strips the alpha channel.  If anything goes
    wrong the original path is returned unchanged (graceful degradation).
    """
    try:
        im = Image.open(image_path)
        # Drop alpha — VLMs don't need it
        if im.mode == "RGBA":
            im = im.convert("RGB")
        elif im.mode != "RGB":
            im = im.convert("RGB")
        im = ImageOps.autocontrast(im, cutoff=1)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        im.save(str(out_path))
        return out_path
    except Exception:
        return image_path



# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


def encode_image_base64(image_path: Path) -> str:
    """Read an image file and return its base64-encoded contents."""
    return base64.b64encode(image_path.read_bytes()).decode("utf-8")
