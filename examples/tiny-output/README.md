# Snapshot tables for the five-vignette corpus

Generated with:

```bash
python3 examples/tfidf_toy.py --corpus examples/tiny-corpus --write-dir examples/tiny-output
```

| file | contents |
| --- | --- |
| `df.tsv` | term and document frequency |
| `idf.tsv` | term and `ln(5 / df)` |
| `tf/*.txt` | normalized TF, alphabetical |
| `tfidf/*.txt` | tf*idf, alphabetical |
| `top_terms.txt` | score-order ranking, top 8 per file |

Regenerate `top_terms.txt` with:

```bash
python3 examples/tfidf_toy.py --corpus examples/tiny-corpus --top 8 \
  > examples/tiny-output/top_terms.txt
```

These files are small enough to diff. If a tokenizer change moves
`soup` off the top of `kitchen.txt`, the snapshot should move with it.
