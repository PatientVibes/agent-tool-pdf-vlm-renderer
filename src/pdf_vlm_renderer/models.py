"""Bounding-box model for VLM detection results."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """A region in a page image, with optional VLM-supplied label + confidence.

    Coordinates are pixel-space, top-left origin (matches Pillow + most
    VLM outputs).
    """

    x_min: int = Field(ge=0)
    y_min: int = Field(ge=0)
    x_max: int = Field(ge=0)
    y_max: int = Field(ge=0)
    label: Optional[str] = None
    confidence: Optional[float] = None

    @property
    def width(self) -> int:
        return self.x_max - self.x_min

    @property
    def height(self) -> int:
        return self.y_max - self.y_min
