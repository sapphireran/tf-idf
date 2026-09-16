# Tests

Standard-library `unittest` coverage for the personal reference
implementation and the tiny corpus.

```bash
python3 -m unittest discover -s tests -v
```

What is locked down:

- tokenizer cleanup (case, punctuation, empty tokens)
- `ln(N / df)` and proportion TF
- the hand-calculated `mats` row in the 3-sentence example
- topical rankings on the five original essays
- a reread of `examples/tiny_corpus/expected/idf.txt`

The Gutenberg `output/` tables are historical fixtures. They are
read by `examples/python/inspect_gutenberg.py` but not regenerated
in CI.
