"""Cursive letter-tracing worksheet generator.

    uv run tracing.py -o out.pdf "The cat sat." "I like trains."
    uv run tracing.py -o out.pdf -f sentences.txt     # one sentence per line
    uv run tracing.py -o out.pdf --header "Name: ________" --header "" --header "Week 1" "The cat sat."
"""
import argparse
from pathlib import Path

from reportlab.lib.colors import Color, black, lightgrey
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from page import ASCENT, MARGIN, PAGE_H, PAGE_W, page_header, spacing

FONTS = Path(__file__).parent / "fonts"
pdfmetrics.registerFont(TTFont("Cursive", FONTS / "LearningCurve.ttf"))
pdfmetrics.registerFont(TTFont("CursiveDashed", FONTS / "LearningCurveDashed.ttf"))

GUIDE = Color(0.6, 0.6, 0.6)


def wrap(text, font, size, width):
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if pdfmetrics.stringWidth(trial, font, size) <= width:
            line = trial
        else:
            lines.append(line)
            line = word
    return lines + [line] if line else lines


def guide_row(c, y, row_h):
    """Three handwriting lines; y is the baseline."""
    c.setStrokeColor(GUIDE)
    c.setLineWidth(1)
    c.setDash()
    c.line(MARGIN, y + row_h, PAGE_W - MARGIN, y + row_h)   # top
    c.setDash(4, 4)
    c.line(MARGIN, y + row_h / 2, PAGE_W - MARGIN, y + row_h / 2)  # midline
    c.setDash()
    c.setStrokeColor(black)
    c.line(MARGIN, y, PAGE_W - MARGIN, y)                   # baseline


def render(c, sentences, blank_rows=0, solid=False, row=0.7, header=()):
    """Draw a tracing worksheet onto canvas c from a fresh page; ends with a page break."""
    if isinstance(sentences, str):
        sentences = [sentences]
    sentences = [s for s in sentences if s.strip()]
    page_header(c, header)
    row_h = row * 72
    font = "Cursive" if solid else "CursiveDashed"
    size = row_h / ASCENT                  # ascenders touch the top line, x-height the midline
    descent, gap, row_total = spacing(row_h)
    width = PAGE_W - 2 * MARGIN - 24       # 12pt padding each side
    y = PAGE_H - MARGIN - row_h

    for sentence in sentences:
        for line in wrap(sentence, font, size, width):
            rows = 1 + blank_rows
            if y - (rows - 1) * row_total - descent < MARGIN:
                c.showPage()
                page_header(c, header)
                y = PAGE_H - MARGIN - row_h
            guide_row(c, y, row_h)
            c.setFont(font, size)
            c.setFillColor(lightgrey if solid else black)
            c.drawString(MARGIN + 12, y, line)
            y -= row_total
            for _ in range(blank_rows):
                guide_row(c, y, row_h)
                y -= row_total
        y -= gap   # extra breathing room between sentences
    c.showPage()


def build(sentences, out, **opts):
    c = canvas.Canvas(str(out), pagesize=letter)
    render(c, sentences, **opts)
    c.save()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("sentences", nargs="*")
    p.add_argument("-f", "--file", type=Path, help="one sentence per line")
    p.add_argument("-o", "--out", default="worksheet.pdf")
    p.add_argument("-b", "--blank-rows", type=int, default=0, help="blank practice rows after each traced line (default 0)")
    p.add_argument("--solid", action="store_true", help="light grey solid letters instead of dashed")
    p.add_argument("--row", type=float, default=0.7, help="writing row height in inches (default 0.7)")
    p.add_argument("--header", action="append", default=[], metavar="TEXT",
                   help="page header text; repeat up to 3 times for left / center / right")
    a = p.parse_args()
    sentences = a.sentences + (a.file.read_text().splitlines() if a.file else [])
    sentences = [s for s in sentences if s.strip()]
    if not sentences:
        p.error("give sentences as arguments or with -f")
    if len(a.header) > 3:
        p.error("--header can be given at most 3 times (left / center / right)")
    build(sentences, a.out, blank_rows=a.blank_rows, solid=a.solid, row=a.row, header=a.header)
    print(a.out)
