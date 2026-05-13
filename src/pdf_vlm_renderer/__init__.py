"""PDF page rendering + VLM preprocessing utilities."""
from .render import (
    pdf_to_page_pngs,
    preprocess_for_vlm,
    encode_image_base64,
    crop_region,
    draw_debug_boxes,
)
from .models import BoundingBox

__all__ = [
    "pdf_to_page_pngs",
    "preprocess_for_vlm",
    "encode_image_base64",
    "crop_region",
    "draw_debug_boxes",
    "BoundingBox",
]
