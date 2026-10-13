"""uv run test_arithmetic.py"""
import random, re, tempfile
from pathlib import Path
from reportlab import rl_config
from arithmetic import CATEGORIES, DIVIDE, MINUS, PLUS, TIMES, build, generate

rl_config.pageCompression = 0   # keep text greppable

D1, D2 = range(10), range(10, 100)
rules = {   # category -> (op, check(a, b))
    "single-add":         (PLUS, lambda a, b: a in D1 and b in D1),
    "single-double-add":  (PLUS, lambda a, b: min(a, b) in D1 and max(a, b) in D2),
    "double-add":         (PLUS, lambda a, b: a in D2 and b in D2),
    "double-sub-single":  (MINUS, lambda a, b: a in D2 and b in D1),
    "single-sub-single":  (MINUS, lambda a, b: a in D1 and b in D1 and a - b >= 0),
    "single-mult":        (TIMES, lambda a, b: a in D1 and b in D1),
    "single-double-mult": (TIMES, lambda a, b: min(a, b) in D1 and max(a, b) in D2),
    "single-div":         (DIVIDE, lambda a, b: a in D2 and b in D1 and b > 1 and a % b == 0),
}
assert set(rules) == set(CATEGORIES)
rng = random.Random(0)
for cat, (op, ok) in rules.items():
    for a, o, b in generate([cat], 500, rng):
        assert o == op and ok(a, b), (cat, a, o, b)

# even mix, no repeats when the pool is big enough, reproducible with a seed
mix = generate(["double-add", "single-div"], 40, random.Random(1))
assert sum(o == PLUS for _, o, _ in mix) == 20
assert len(set(mix)) == 40
assert mix == generate(["double-add", "single-div"], 40, random.Random(1))

out = Path(tempfile.mkdtemp()) / "m.pdf"
build(["single-mult"], out, title="Times", seed=5)
pdf = out.read_bytes()
assert re.search(rb"/Count 1\b", pdf), "default count fills one page"
assert pdf.count(b"(Times) Tj") == 1
n = len(re.findall(rb"\\327 \d+ =\) Tj", pdf))   # \327 = multiplication sign
assert n >= 10 and n % 2 == 0, n

build(["single-add"], out, count=50, title="Lots", header="Week 1")
pdf = out.read_bytes()
pages = int(re.search(rb"/Count (\d+)", pdf).group(1))
assert pages > 1 and pdf.count(b"(Lots) Tj") == pdf.count(b"(Week 1) Tj") == pages
assert len(re.findall(rb"\+ \d+ =\) Tj", pdf)) == 50

for bad in [dict(categories=[]), dict(categories=["nope"]), dict(categories="single-add", count=0)]:
    try:
        build(bad.pop("categories"), out, **bad)
    except ValueError:
        pass
    else:
        raise AssertionError(bad)
print("ok")
