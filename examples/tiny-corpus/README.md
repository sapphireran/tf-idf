# Tiny TF-IDF corpus

Three six-word documents used as a pocket version of the Gutenberg experiment.

| file | text | distinctive terms after TF-IDF |
| --- | --- | --- |
| `docs/cats.txt` | the cat sat on the mat | cat, mat |
| `docs/dogs.txt` | the dog sat on the log | dog, log |
| `docs/birds.txt` | a bird sat on the nest | a, bird, nest |

Shared words `the`, `sat`, and `on` have `df = 3` and `idf = 0`.

- Arithmetic: [walkthrough.md](walkthrough.md)
- Precomputed tables: [expected/](expected/)
- Regenerator: `python3 examples/python/tfidf_example.py`

```bash
# from the repository root
python3 examples/python/tfidf_example.py \
  --input-dir examples/tiny-corpus/docs \
  --output-dir /tmp/tiny-tfidf

diff -u examples/tiny-corpus/expected/idf.txt /tmp/tiny-tfidf/idf.txt
diff -ur examples/tiny-corpus/expected/tf /tmp/tiny-tfidf/tf
diff -ur examples/tiny-corpus/expected/tfidf /tmp/tiny-tfidf/tfidf
```

The unit test in `examples/python/test_tfidf_example.py` asserts the same identities without going through the shell.
