.PHONY: test clean

# make worksheet.pdf S="The cat sat." or: make worksheet.pdf F=sentences.txt
%.pdf:
	uv run tracing.py -o $@ $(if $(F),-f $(F)) $(S)

example:
	uv run tracing.py -o example.pdf "In a hole in the ground there lived a hobbit."

test:
	uv run test_tracing.py

clean:
	rm -rf *.pdf __pycache__
