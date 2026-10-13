"""Number-pattern worksheets: one random pattern per line, the first numbers shown, 3 blanks to fill in.

    uv run patterns.py -o out.pdf --title "What comes next?"
    uv run patterns.py -o out.pdf -n 12 --seed 7

Patterns, each picked at random (X, Y from 1-10; starting from a random single digit unless noted):
add X each step; subtract X each step (from a two-digit start, never negative);
alternate adding X then Y; Fibonacci (1, 1, 2, 3, 5, 8, ...: one extra number shown).
"""
import argparse
import random

from reportlab.lib.colors import black
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

from page import MARGIN, PAGE_W, SANS, sans_layout, start_page

SHOWN, BLANKS = 5, 3


def add(rng):
    x, n = rng.randint(1, 10), rng.randint(0, 9)
    return [n + i * x for i in range(SHOWN + BLANKS)]


def subtract(rng):
    x = rng.randint(1, 10)
    n = rng.randint(max(10, (SHOWN + BLANKS - 1) * x), 99)   # last term stays >= 0
    return [n - i * x for i in range(SHOWN + BLANKS)]


def alternate(rng):
    x, y = rng.sample(range(1, 11), 2)                      # x != y, or it's just add
    seq = [rng.randint(0, 9)]
    for i in range(SHOWN + BLANKS - 1):
        seq.append(seq[-1] + (x, y)[i % 2])
    return seq


def fibonacci(rng):
    seq = [1, 1]
    while len(seq) < SHOWN + 1 + BLANKS:                       # one extra shown: 1, 1 alone gives little away
        seq.append(seq[-1] + seq[-2])
    return seq


PATTERNS = [add, subtract, alternate, fibonacci]


def generate(count, rng):
    """count full sequences (answers included), each a random pattern, avoiding repeats where possible."""
    seen, seqs = set(), []
    for _ in range(count):
        for _ in range(100):
            seq = tuple(rng.choice(PATTERNS)(rng))
            if seq not in seen:
                break
        seen.add(seq)
        seqs.append(list(seq))
    return seqs


def render(c, count=None, seed=None, title=None, row=0.7, header=()):
    """Draw a number-pattern worksheet onto canvas c from a fresh page; ends with a page break.

    count defaults to one full page."""
    if count is not None and (not isinstance(count, int) or count < 1):
        raise ValueError(f"count must be a positive integer, got {count!r}")
    row_h, size, top, pitch, rows = sans_layout(row, title)
    seqs = generate(count or rows, random.Random(seed))

    # Flow each row like text, "48, 43, 38, ____, ____": blanks get room for a handwritten 2-digit
    # answer, shrinking the font if the widest row wouldn't otherwise fit.
    width = PAGE_W - 2 * MARGIN - 24       # 12pt padding each side, like the cursive sheets
    def shown_w(seq, size):
        return (sum(stringWidth(str(n), SANS, size) for n in seq[:-BLANKS])
                + stringWidth(", ", SANS, size) * (len(seq) - 1))
    widest = max(seqs, key=lambda seq: shown_w(seq, size))
    digit = stringWidth("0", SANS, size)
    size *= min(1, width / (shown_w(widest, size) + BLANKS * 2.5 * digit))
    digit, sep = stringWidth("0", SANS, size), stringWidth(", ", SANS, size)
    blank = min(3 * digit, (width - shown_w(widest, size)) / BLANKS)

    for i, seq in enumerate(seqs):
        r = i % rows
        if i and r == 0:
            c.showPage()
        if r == 0:
            start_page(c, header, title, row_h)
        y = top - row_h - r * pitch
        x = MARGIN + 12
        c.setFont(SANS, size)
        c.setFillColor(black)
        c.setStrokeColor(black)
        c.setLineWidth(1)
        c.setDash()
        for j, n in enumerate(seq):
            if j < len(seq) - BLANKS:
                c.drawString(x, y, str(n))
                x += stringWidth(str(n), SANS, size)
            else:
                c.line(x, y, x + blank, y)
                x += blank
            if j < len(seq) - 1:
                c.drawString(x, y, ",")
                x += sep
    c.showPage()


def build(out, **opts):
    c = canvas.Canvas(str(out), pagesize=letter)
    render(c, **opts)
    c.save()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("-o", "--out", default="worksheet.pdf")
    p.add_argument("-n", "--count", type=int, help="number of patterns (default: one full page)")
    p.add_argument("--title")
    p.add_argument("--seed", type=int, help="random seed, for a reproducible sheet")
    p.add_argument("--row", type=float, default=0.7, help="row height in inches (default 0.7)")
    p.add_argument("--header", action="append", default=[], metavar="TEXT",
                   help="page header text; repeat up to 3 times for left / center / right")
    a = p.parse_args()
    try:
        build(a.out, count=a.count, seed=a.seed, title=a.title, row=a.row, header=a.header)
    except ValueError as e:
        p.error(str(e))
    print(a.out)
