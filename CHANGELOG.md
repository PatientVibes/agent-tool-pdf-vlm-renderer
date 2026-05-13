# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-05-12

### Added
- Initial release, extracted from `agent-harness-card-extractor`'s `card_extractor/rendering.py`.
- `pdf_to_page_pngs(pdf_path, out_dir, dpi=300)` — pypdfium2-based PDF rasterization.
- `preprocess_for_vlm(image_path, out_path)` — RGB conversion + `ImageOps.autocontrast` for degraded scans; graceful fallback returns the original path on error.
- `encode_image_base64(image_path)` — inline base64 encoding for VLM payloads.
- `crop_region(image_path, box, out_path, pad_px=10)` — pixel-space `BoundingBox` crop with padding and bounds clamping.
- `draw_debug_boxes(image_path, boxes, out_path, line_width=None)` — labeled outline overlay for visual QA.
- `BoundingBox` pydantic model — pixel-space (`x_min`, `y_min`, `x_max`, `y_max`) + optional `label` and `confidence`, with `width` / `height` properties.

### Changed (from card-extractor source)
- Genericized for any document type: `card_type` Literal removed in favor of free-form `label: Optional[str]`.
- Coordinates switched from normalized `[0, 1]` floats to pixel-space ints — matches Pillow and most VLM tool outputs directly, no `norm_to_px` conversion needed.
- Dropped `crop_front_boxes` helper (card-specific) — callers can filter `boxes` by `label` themselves.
