# Expected output for the tiny corpus

Regenerate:

```bash
python3 examples/python/compute_tfidf.py \
  --input-dir examples/tiny-corpus \
  --output-dir examples/tiny-corpus-expected
```

Top of each TF-IDF file should look like:

- `cats.txt`: purr, cat, cats, sofa, whiskers, yarn
- `dogs.txt`: bark, dog, dogs, ears, garden, yard
- `baking.txt`: dough, bread, flour, ovens
