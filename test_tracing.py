"""uv run test_tracing.py"""
import re, tempfile
from pathlib import Path
from reportlab import rl_config
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

# header repeats on every page (uncompressed so the text is greppable)
rl_config.pageCompression = 0
build(["The quick brown fox jumps over the lazy dog."] * 4, str(out), blank_rows=1,
      header=["Name: ____", "", "Week 1"])
pdf = out.read_bytes()
pages = int(re.search(rb"/Count (\d+)", pdf).group(1))
assert pages > 1, pages
assert pdf.count(b"(Week 1) Tj") == pages
assert pdf.count(b"(Name: ____) Tj") == pages
print("ok")
