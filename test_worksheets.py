"""uv run test_worksheets.py"""
import re, tempfile
from pathlib import Path
from reportlab import rl_config
from worksheets import build, load

rl_config.pageCompression = 0   # keep text greppable

out = Path(tempfile.mkdtemp()) / "set.pdf"
build({
    "defaults": {"header": ["Name: ____", "", "Week 1"], "blank_rows": 1},
    "worksheets": [
        {"type": "tracing", "sentences": ["The cat sat."]},
        {"type": "tracing", "sentences": ["I like trains."], "solid": True, "header": "Bonus"},
        {"type": "math", "categories": ["single-add"], "count": 4, "title": "Sums"},
        {"type": "patterns", "count": 3},
    ],
}, out)
pdf = out.read_bytes()
assert re.search(rb"/Count 4\b", pdf), "each worksheet starts its own page"
assert pdf.count(b"(Week 1) Tj") == 3, "defaults reach every type"
assert pdf.count(b"(Sums) Tj") == 1
assert pdf.count(b"(Bonus) Tj") == 1, "worksheet header overrides defaults"

for bad, msg in [
    ({}, "worksheets"),
    ({"worksheets": []}, "worksheets"),
    ({"worksheets": [{"type": "nope"}]}, "type"),
    ({"worksheets": [{"type": "tracing"}]}, "missing"),
    ({"worksheets": [{"type": "tracing", "sentences": ["x"], "blnk_rows": 1}]}, "blnk_rows"),
    ({"defaults": {"colour": 1}, "worksheets": [{"type": "tracing", "sentences": ["x"]}]}, "colour"),
    ({"worksheet": []}, "worksheets"),
    ({"defaults": [], "worksheets": [{"type": "tracing", "sentences": ["x"]}]}, "defaults"),
    ({"worksheets": ["The cat sat."]}, "object"),
    ({"worksheets": [{"type": "math", "categories": ["x"], "solid": True}]}, "solid"),
    ({"worksheets": [{"type": "math"}]}, "missing"),
]:
    try:
        load(bad)
    except ValueError as e:
        assert msg in str(e), (bad, e)
    else:
        raise AssertionError(f"accepted {bad}")
print("ok")
