"""Build a set of worksheets from one JSON file into a single PDF; each worksheet starts on a new page.

    uv run worksheets.py week1.json               # -> week1.pdf
    uv run worksheets.py week1.json -o out.pdf

    {
      "defaults": {"header": ["Name: ________", "", "Week 1"]},
      "worksheets": [
        {"type": "tracing", "sentences": ["The cat sat.", "I like trains."]},
        {"type": "tracing", "sentences": ["Bonus round!"], "solid": true, "blank_rows": 1},
        {"type": "math", "title": "Times Tables", "categories": ["single-mult"], "count": 12}
      ]
    }

"defaults" apply to every worksheet whose type accepts them; a worksheet's own keys win.
"""
import argparse
import inspect
import json
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

import arithmetic
import tracing

# type name -> render(c, **options); options are the function's keyword parameters
TYPES = {"tracing": tracing.render, "math": arithmetic.render}


def options(render):
    """(all, required) option names for a render function."""
    ps = list(inspect.signature(render).parameters.values())[1:]   # skip the canvas
    return {p.name for p in ps}, {p.name for p in ps if p.default is p.empty}


def load(spec):
    """Validate a parsed set spec; return [(render, kwargs), ...] in order."""
    if not isinstance(spec, dict) or not isinstance(spec.get("worksheets"), list) or not spec["worksheets"]:
        raise ValueError('expected an object with a non-empty "worksheets" list')
    if bad := set(spec) - {"defaults", "worksheets"}:
        raise ValueError(f"unknown top-level key(s) {sorted(bad)}")
    defaults = spec.get("defaults", {})
    if not isinstance(defaults, dict):
        raise ValueError('"defaults" must be an object')
    if bad := set(defaults) - set().union(*(options(r)[0] for r in TYPES.values())):
        raise ValueError(f"defaults: unknown option(s) {sorted(bad)}")

    jobs = []
    for i, sheet in enumerate(spec["worksheets"], 1):
        if not isinstance(sheet, dict):
            raise ValueError(f"worksheet {i}: expected an object, got {sheet!r}")
        sheet = dict(sheet)
        kind = sheet.pop("type", None)
        if kind not in TYPES:
            raise ValueError(f"worksheet {i}: type must be one of {sorted(TYPES)}, got {kind!r}")
        render = TYPES[kind]
        known, required = options(render)
        if bad := set(sheet) - known:
            raise ValueError(f"worksheet {i} ({kind}): unknown option(s) {sorted(bad)}")
        opts = {k: v for k, v in defaults.items() if k in known} | sheet
        if missing := required - set(opts):
            raise ValueError(f"worksheet {i} ({kind}): missing {sorted(missing)}")
        jobs.append((render, opts))
    return jobs


def build(spec, out):
    jobs = load(spec)
    c = canvas.Canvas(str(out), pagesize=letter)
    for render, opts in jobs:
        render(c, **opts)
    c.save()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("set", type=Path, help="JSON worksheet set")
    p.add_argument("-o", "--out", type=Path, help="output PDF (default: <set>.pdf)")
    a = p.parse_args()
    try:
        build(json.loads(a.set.read_text()), a.out or a.set.with_suffix(".pdf"))
    except (json.JSONDecodeError, ValueError) as e:
        p.error(f"{a.set}: {e}")
    print(a.out or a.set.with_suffix(".pdf"))
