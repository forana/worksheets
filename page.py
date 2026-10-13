"""Shared page layout: Letter size, margins, row spacing, printout-style running header, titles."""
from reportlab.lib.colors import Color, black
from reportlab.lib.pagesizes import letter

PAGE_W, PAGE_H = letter
MARGIN = 54            # 3/4 inch
HEADER = Color(0.35, 0.35, 0.35)
SANS, SANS_BOLD = "Helvetica", "Helvetica-Bold"
# Learning Curve (cursive) metrics, fraction of font size: ascender/caps 0.60, x-height 0.30, descender 0.24.
# Every sheet uses its row spacing so they all look alike.
ASCENT, DESCENT = 0.60, 0.24


def spacing(row_h):
    """(descent, gap, pitch) for writing rows of height row_h; pitch is baseline to baseline."""
    descent = row_h / ASCENT * DESCENT     # room for cursive descenders below the baseline
    gap = row_h / 6                        # 3 trace+practice pairs fit a Letter page at 1in rows
    return descent, gap, row_h + descent + gap


def sans_layout(row, title):
    """Rows for the sans-serif sheets, spaced like the cursive ones, below an optional title.

    Returns (row_h, size, top, pitch, rows): font size, top of the first row, rows per page."""
    row_h = row * 72
    descent, gap, pitch = spacing(row_h)
    top = PAGE_H - MARGIN - (row_h / 2 + gap if title else 0)
    rows = 1 + int((top - row_h - descent - MARGIN) // pitch)
    return row_h, row_h * 0.7, top, pitch, rows   # digits reach about the cursive midline


def page_header(c, header):
    """Printout-style running header in the top margin: up to 3 values, left / center / right."""
    if isinstance(header, str):
        header = [header]
    if len(header) > 3:
        raise ValueError("header takes at most 3 values (left / center / right)")
    if not header:
        return
    c.setFont("Helvetica", 9)
    c.setFillColor(HEADER)
    y = PAGE_H - 36
    left, center, right = (list(header) + ["", "", ""])[:3]
    c.drawString(MARGIN, y, left)
    c.drawCentredString(PAGE_W / 2, y, center)
    c.drawRightString(PAGE_W - MARGIN, y, right)


def start_page(c, header, title, row_h):
    """Running header plus an optional centered bold title, sized to sit above sans_layout's rows."""
    page_header(c, header)
    if title:
        size = row_h / 2
        c.setFont(SANS_BOLD, size)
        c.setFillColor(black)
        c.drawCentredString(PAGE_W / 2, PAGE_H - MARGIN - size * 0.75, title)
