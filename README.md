# worksheets

Printable worksheet generator (currently: cursive letter-tracing). Letter-size PDF.

```sh
uv run tracing.py -o week1.pdf "The cat sat on the mat." "I like trains."
uv run tracing.py -o week1.pdf -f sentences.txt   # one sentence per line
```

Options: `-b 1` to add a blank practice row after each traced line (default 0), `--row 0.75` row height in inches (default 1.0), `--solid` light-grey solid letters instead of dashed.

Font: Learning Curve by Blue Vinyl Fonts, free for private use (`fonts/LICENSE-LearningCurve.txt`).

Check: `uv run test_tracing.py`

See [./example.pdf](example).
