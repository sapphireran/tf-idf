# Tests

Standard-library checks for the personal examples. They do not rerun the 2012 Perl scripts or overwrite `output/`.

```bash
python3 -m unittest discover -s tests -v
```

| File | What it locks |
| --- | --- |
| `test_tokenizer.py` | Normalizer, apostrophe stripping, empty-token denominator |
| `test_tiny_corpus.py` | Hand-worked `tf` / `idf` / cosine on the three-document toy |
| `test_committed_output.py` | Snapshot shape, `ln(18/df)`, Alice, the dirty `thatyou` cell |
| `test_similarity.py` | Orthogonal zero-IDF pairs and query IDF |

Run a single file with:

```bash
python3 tests/test_tiny_corpus.py
```
