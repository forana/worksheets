"""Arithmetic worksheets: two columns of random problems with blank answer lines.

    uv run arithmetic.py -o out.pdf single-double-mult
    uv run arithmetic.py -o out.pdf single-add single-sub-single --count 20 --title "Adding & Subtracting"

Several categories make an even mix, shuffled. --seed makes a sheet reproducible.
"""
import argparse
import random

from reportlab.lib.colors import black
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

from page import MARGIN, PAGE_H, PAGE_W, page_header
from tracing import spacing

FONT, TITLE_FONT = "Helvetica", "Helvetica-Bold"
PLUS, MINUS, TIMES, DIVIDE = "+", "–", "×", "÷"   # en dash reads as a minus sign in Helvetica
COL_GAP = 36           # between the two columns


def digit(rng, lo=0):
    return rng.randint(lo, 9)


def double(rng):
    return rng.randint(10, 99)


def swap(rng, a, op, b):
    """Commutative ops: show the operands in either order."""
    return (a, op, b) if rng.random() < 0.5 else (b, op, a)


def single_sub_single(rng):
    a, b = digit(rng), digit(rng)
    return max(a, b), MINUS, min(a, b)       # never negative


def single_div(rng):
    d = rng.randint(2, 9)                    # dividing by 1 is trivial
    q = rng.randint(-(-10 // d), 99 // d)    # two-digit dividend, whole-number answer
    return d * q, DIVIDE, d


# category -> rng -> (a, op, b). Multiplication skips 0 and 1 as the single digit: they're trivial.
CATEGORIES = {
    "single-add":         lambda r: (digit(r), PLUS, digit(r)),
    "single-double-add":  lambda r: swap(r, digit(r), PLUS, double(r)),
    "double-add":         lambda r: (double(r), PLUS, double(r)),
    "double-sub-single":  lambda r: (double(r), MINUS, digit(r)),
    "single-sub-single":  single_sub_single,
    "single-mult":        lambda r: (digit(r, 2), TIMES, digit(r, 2)),
    "single-double-mult": lambda r: swap(r, digit(r, 2), TIMES, double(r)),
    "single-div":         single_div,
}


def generate(categories, count, rng):
    """count problems, an even mix of categories in random order, avoiding repeats where possible."""
    seen, problems = set(), []
    for i in range(count):
        make = CATEGORIES[categories[i % len(categories)]]
        for _ in range(100):
            p = make(rng)
            if p not in seen:
                break
        seen.add(p)
        problems.append(p)
    rng.shuffle(problems)
    return problems


def render(c, categories, count=None, seed=None, title=None, row=0.7, header=()):
    """Draw an arithmetic worksheet onto canvas c from a fresh page; ends with a page break.

    count defaults to one full page."""
    if isinstance(categories, str):
        categories = [categories]
    if not categories:
        raise ValueError("need at least one category")
    if bad := [k for k in categories if k not in CATEGORIES]:
        raise ValueError(f"unknown category {bad}; choose from {list(CATEGORIES)}")
    if count is not None and (not isinstance(count, int) or count < 1):
        raise ValueError(f"count must be a positive integer, got {count!r}")

    row_h = row * 72
    descent, gap, pitch = spacing(row_h)     # same rows as the cursive sheets
    size = row_h * 0.7                       # digits reach about the cursive midline
    title_size = row_h / 2
    top = PAGE_H - MARGIN - (title_size + gap if title else 0)
    rows = 1 + int((top - row_h - descent - MARGIN) // pitch)
    count = count or 2 * rows
    problems = [f"{a} {op} {b} =" for a, op, b in generate(categories, count, random.Random(seed))]

    col_w = (PAGE_W - 2 * MARGIN - COL_GAP) / 2
    expr_w = max(stringWidth(p, FONT, size) for p in problems)   # line up the = signs
    for i, problem in enumerate(problems):
        r, col = divmod(i % (2 * rows), 2)
        if i and r == col == 0:
            c.showPage()
        if r == col == 0:
            page_header(c, header)
            if title:
                c.setFont(TITLE_FONT, title_size)
                c.setFillColor(black)
                c.drawCentredString(PAGE_W / 2, PAGE_H - MARGIN - title_size * 0.75, title)
        x = MARGIN + col * (col_w + COL_GAP)
        y = top - row_h - r * pitch
        c.setFont(FONT, size)
        c.setFillColor(black)
        c.drawRightString(x + expr_w, y, problem)
        c.setStrokeColor(black)
        c.setLineWidth(1)
        c.setDash()
        c.line(x + expr_w + size / 4, y, x + col_w, y)
    c.showPage()


def build(categories, out, **opts):
    c = canvas.Canvas(str(out), pagesize=letter)
    render(c, categories, **opts)
    c.save()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("categories", nargs="+", choices=list(CATEGORIES), metavar="CATEGORY",
                   help=", ".join(CATEGORIES))
    p.add_argument("-o", "--out", default="worksheet.pdf")
    p.add_argument("-n", "--count", type=int, help="number of problems (default: one full page)")
    p.add_argument("--title")
    p.add_argument("--seed", type=int, help="random seed, for a reproducible sheet")
    p.add_argument("--row", type=float, default=0.7, help="row height in inches (default 0.7)")
    p.add_argument("--header", action="append", default=[], metavar="TEXT",
                   help="page header text; repeat up to 3 times for left / center / right")
    a = p.parse_args()
    try:
        build(a.categories, a.out, count=a.count, seed=a.seed, title=a.title, row=a.row, header=a.header)
    except ValueError as e:
        p.error(str(e))
    print(a.out)
