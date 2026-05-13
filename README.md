# agent-tool-pdf-vlm-renderer

Render PDF pages to VLM-ready PNGs and prep bounding-box crops for inline base64 payloads.

Extracted from [`agent-harness-card-extractor`](https://github.com/PatientVibes/agent-harness-card-extractor)'s `card_extractor/rendering.py` and genericized — `card_type` is now a free-form `label`, coordinates are pixel-space instead of normalized.

## Install

```bash
uv tool install --editable D:/agent-tool-pdf-vlm-renderer
# or, as a library dep:
uv add agent-tool-pdf-vlm-renderer
```

## What it does

| Function | Purpose |
|---|---|
| `pdf_to_page_pngs(pdf_path, out_dir, dpi=300)` | Rasterize each page of a PDF to a PNG via pypdfium2 (Apache-2.0). |
| `preprocess_for_vlm(image_path, out_path)` | Drop alpha, run `ImageOps.autocontrast(cutoff=1)` to rescue degraded scans. Returns the original path unchanged on any error (graceful degradation). |
| `encode_image_base64(image_path)` | Read an image and return its base64-encoded string for inline VLM payloads. |
| `crop_region(image_path, box, out_path, pad_px=10)` | Crop a pixel-space `BoundingBox` region with padding; clamps to image bounds; returns `None` if the box collapses. |
| `draw_debug_boxes(image_path, boxes, out_path, line_width=None)` | Overlay numbered, labeled rectangles for visual QA. `Front` → lime, `Back` → red, others cycle through yellow/cyan/magenta/orange. |

## `BoundingBox`

Pixel-space, top-left origin (matches Pillow + most VLM outputs):

```python
from pdf_vlm_renderer import BoundingBox

box = BoundingBox(
    x_min=120, y_min=80, x_max=540, y_max=360,
    label="Front",          # optional, any string
    confidence=0.92,         # optional
)
box.width   # 420
box.height  # 280
```

## Example

```python
from pathlib import Path
from pdf_vlm_renderer import (
    pdf_to_page_pngs,
    preprocess_for_vlm,
    crop_region,
    encode_image_base64,
    BoundingBox,
)

# 1. Rasterize
pages = pdf_to_page_pngs(Path("scan.pdf"), Path("out/pages"), dpi=300)

# 2. (Hand-wave) ask a VLM for boxes…
boxes = [BoundingBox(x_min=120, y_min=80, x_max=540, y_max=360, label="Front")]

# 3. Crop + preprocess + encode for the next VLM call
for i, b in enumerate(boxes, start=1):
    crop_path = crop_region(pages[0], b, Path(f"out/crop_{i}.png"))
    if crop_path is None:
        continue
    clean = preprocess_for_vlm(crop_path, Path(f"out/crop_{i}_clean.png"))
    payload_b64 = encode_image_base64(clean)
```

## Dependencies

- [`pypdfium2`](https://github.com/pypdfium2-team/pypdfium2) — Apache-2.0, PDF rasterization.
- [`Pillow`](https://python-pillow.org/) — HPND, image manipulation.
- [`pydantic`](https://docs.pydantic.dev/) — `BoundingBox` model.

## Provenance

Phase 3 of the agent-toolbox extraction (2026-05-12). Sibling tools:

- [`agent-tool-llm-utils`](https://github.com/PatientVibes/agent-tool-llm-utils)
- [`agent-tool-token-tracker`](https://github.com/PatientVibes/agent-tool-token-tracker)

## License

MIT — see [`LICENSE`](LICENSE).
