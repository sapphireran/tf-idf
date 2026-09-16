# Expected output for the micro corpus

Regenerate:

```bash
python3 examples/python/compute_tfidf.py \
  --input-dir examples/micro-corpus \
  --output-dir examples/micro-corpus-expected
```

`idf.txt` must match the table in
[../../docs/worked-example.md](../../docs/worked-example.md):
`ln(3)` for one-document terms, `ln(3/2)` for `the` / `sat` / `on`.
