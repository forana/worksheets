"""Shared page layout: Letter size, margins, printout-style running header."""
from reportlab.lib.colors import Color
from reportlab.lib.pagesizes import letter

PAGE_W, PAGE_H = letter
MARGIN = 54            # 3/4 inch
HEADER = Color(0.35, 0.35, 0.35)


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
