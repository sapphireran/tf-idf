# tiny-output

Tables written by `python3 examples/tiny_tfidf.py` from `examples/tiny-corpus/`.
Same tab-separated shape as the Gutenberg `output/` snapshot: `df.txt`,
`idf.txt`, `tf/<doc>.txt`, `tfidf/<doc>.txt`.

Safe to delete and regenerate. The `--check` flag on `tiny_tfidf.py`
asserts the top-term scores, not these files.
