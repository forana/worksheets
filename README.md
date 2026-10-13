# worksheets

Printable worksheet generator (currently: cursive letter-tracing). Letter-size PDF.

```sh
uv run tracing.py -o week1.pdf "The cat sat on the mat." "I like trains."
uv run tracing.py -o week1.pdf -f sentences.txt   # one sentence per line
uv run tracing.py -o week1.pdf --header "Name: ________" --header "Cursive" --header "Week 1" -f sentences.txt
```

Options: `-b 1` to add a blank practice row after each traced line (default 0), `--row 1.0` row height in inches (default 0.7), `--solid` light-grey solid letters instead of dashed, `--header TEXT` printout-style page header — repeat up to 3 times for left / center / right slots (pass `""` to skip a slot).

Font: Learning Curve by Blue Vinyl Fonts, free for private use (`fonts/LICENSE-LearningCurve.txt`).

Check: `uv run test_tracing.py`

See [./example.pdf](example).
