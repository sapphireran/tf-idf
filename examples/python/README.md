# Python teaching copies

Two small programs that sit next to the Perl scripts instead of replacing them.

| script | job |
| --- | --- |
| `tfidf_example.py` | tokenize → TF → DF → IDF → TF-IDF, write the same TSV shapes |
| `extract_top_terms.py` | sort an existing TSV by score |

## `tfidf_example.py`

```bash
# default paths are the tiny corpus
python3 examples/python/tfidf_example.py

# any directory of one-file-per-document texts
python3 examples/python/tfidf_example.py \
  --input-dir examples/excerpts \
  --output-dir /tmp/excerpt-tfidf

# Gutenberg collection, without touching committed output/
python3 examples/python/tfidf_example.py \
  --input-dir gutenberg \
  --output-dir /tmp/gutenberg-tfidf
```

`--n` overrides the collection size if you want to see what the Perl `$#files` quirk would do. `--no-write` prints the per-document heads only.

Formulas are documented in [../../docs/algorithm.md](../../docs/algorithm.md). Tokenization is documented in [../../docs/tokenization.md](../../docs/tokenization.md).

## `extract_top_terms.py`

```bash
python3 examples/python/extract_top_terms.py output/tfidf/carroll-alice.txt -n 20
python3 examples/python/extract_top_terms.py --tf output/tf/carroll-alice.txt
python3 examples/python/extract_top_terms.py --zeros output/tfidf/melville-moby_dick.txt
python3 examples/python/extract_top_terms.py --bottom output/tfidf/carroll-alice.txt -n 8
```

`--zeros` counts exact `0.0` rows (the collection-wide words). `--bottom` is useful for confirming that those zeros sit together.

## Tests

```bash
python3 -m unittest examples.python.test_tfidf_example examples.python.test_extract_top_terms
```

If your working directory is `examples/python/`, use:

```bash
python3 -m unittest test_tfidf_example test_extract_top_terms
```
