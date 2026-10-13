# worksheets

Printable worksheet generator (currently: cursive letter-tracing). Letter-size PDF.

```sh
uv run tracing.py -o week1.pdf "The cat sat on the mat." "I like trains."
uv run tracing.py -o week1.pdf -f sentences.txt   # one sentence per line
uv run tracing.py -o week1.pdf --header "Name: ________" --header "Cursive" --header "Week 1" -f sentences.txt
```

Options: `-b 1` to add a blank practice row after each traced line (default 0), `--row 1.0` row height in inches (default 0.7), `--solid` light-grey solid letters instead of dashed, `--header TEXT` printout-style page header — repeat up to 3 times for left / center / right slots (pass `""` to skip a slot).

## Worksheet sets

Build several worksheets into one PDF (each starts on a new page) from a JSON file — see [example.json](example.json):

```sh
uv run worksheets.py week1.json            # -> week1.pdf
make week1.pdf                             # same thing
```

```json
{
  "defaults": {"header": ["Name: ________", "", "Week 1"]},
  "worksheets": [
    {"type": "tracing", "sentences": ["The cat sat.", "I like trains."]},
    {"type": "tracing", "sentences": ["Bonus round!"], "solid": true, "blank_rows": 1}
  ]
}
```

Each worksheet has a `type` (currently just `tracing`) plus that type's options. Tracing options mirror the CLI: `sentences`, `blank_rows`, `solid`, `row` (inches), `header` (a string or up to 3 strings for left / center / right). `defaults` apply to every worksheet that accepts them; a worksheet's own keys override them. Unknown keys are errors, so typos don't silently do nothing.

Font: Learning Curve by Blue Vinyl Fonts, free for private use (`fonts/LICENSE-LearningCurve.txt`).

Check: `make test`

See [./example.pdf](example).
