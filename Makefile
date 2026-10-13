.PHONY: test clean

# make week1.pdf, built from week1.json if it exists
%.pdf: %.json
	uv run worksheets.py -o $@ $<

# make worksheet.pdf S="The cat sat." or: make worksheet.pdf F=sentences.txt
%.pdf:
	uv run tracing.py -o $@ $(if $(F),-f $(F)) $(if $(S),"$$S")

example:
	uv run tracing.py -o example.pdf "In a hole in the ground there lived a hobbit."

test:
	uv run test_tracing.py
	uv run test_worksheets.py

clean:
	rm -rf *.pdf __pycache__
