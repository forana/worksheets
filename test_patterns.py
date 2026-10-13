"""uv run test_patterns.py"""
import random, re, tempfile
from pathlib import Path
from reportlab import rl_config
from patterns import BLANKS, SHOWN, build, generate

rl_config.pageCompression = 0   # keep text greppable

FIB = [1, 1, 2, 3, 5, 8, 13, 21, 34]
kinds = set()
for seq in generate(2000, random.Random(0)):
    steps = [b - a for a, b in zip(seq, seq[1:])]
    assert min(seq) >= 0, seq
    if seq == FIB:
        kinds.add("fibonacci")
        continue
    assert len(seq) == SHOWN + BLANKS, seq
    if len(set(steps)) == 1 and steps[0] > 0:
        kinds.add("add")
        assert seq[0] <= 9 and steps[0] <= 10, seq
    elif len(set(steps)) == 1:
        kinds.add("subtract")
        assert 10 <= seq[0] <= 99 and -steps[0] <= 10, seq
    else:
        kinds.add("alternate")
        x, y = steps[0], steps[1]
        assert seq[0] <= 9 and x != y and 1 <= x <= 10 and 1 <= y <= 10, seq
        assert steps == [x, y] * 3 + [x], seq
assert kinds == {"add", "subtract", "alternate", "fibonacci"}, kinds

sheet = generate(8, random.Random(1))
assert len({tuple(s) for s in sheet}) == 8, "no repeats, so Fibonacci at most once"
assert sheet == generate(8, random.Random(1)), "seeded sheets are reproducible"

out = Path(tempfile.mkdtemp()) / "p.pdf"
for row in (0.5, 0.7, 1.0):
    build(out, title="Next?", header="Week 1", count=20, seed=2, row=row)
    pdf = out.read_bytes()
    pages = int(re.search(rb"/Count (\d+)", pdf).group(1))
    assert pages > 1 and pdf.count(b"(Next?) Tj") == pdf.count(b"(Week 1) Tj") == pages
    # 3 blank lines per pattern, all inside the page margins
    lines = [tuple(map(float, m)) for m in re.findall(rb"([\d.]+) ([\d.]+) m ([\d.]+) ([\d.]+) l S", pdf)]
    assert len(lines) == 20 * BLANKS, len(lines)
    assert all(54 <= x1 < x2 <= 612 - 54 for x1, _, x2, _ in lines), row

build(out)
assert re.search(rb"/Count 1\b", out.read_bytes()), "default count fills one page"
try:
    build(out, count=0)
except ValueError:
    pass
else:
    raise AssertionError("count=0 accepted")
print("ok")
