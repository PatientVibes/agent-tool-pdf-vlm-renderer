"""Test fixtures."""
from pathlib import Path

import pytest
from reportlab.pdfgen import canvas


@pytest.fixture
def tiny_pdf(tmp_path: Path) -> Path:
    """Generate a 2-page A4 test PDF on the fly."""
    p = tmp_path / "tiny.pdf"
    c = canvas.Canvas(str(p))
    c.drawString(100, 750, "Page 1")
    c.showPage()
    c.drawString(100, 750, "Page 2")
    c.showPage()
    c.save()
    return p
