"""uv run test_tracing.py"""
import re, tempfile
from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from tracing import build, wrap

for line in wrap("The quick brown fox jumps over the lazy dog.", "CursiveDashed", 120, 504):
    assert pdfmetrics.stringWidth(line, "CursiveDashed", 120) <= 504, line
assert wrap("", "Cursive", 12, 100) == []

out = Path(tempfile.mkdtemp()) / "t.pdf"
build(["The quick brown fox jumps over the lazy dog.", "I like trains."], str(out))
pdf = out.read_bytes()
assert pdf.startswith(b"%PDF")
assert re.search(rb"/Count 1\b", pdf), "expected 6 traced lines -> 1 page"
print("ok")
