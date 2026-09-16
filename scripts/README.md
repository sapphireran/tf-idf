# Ranking helper

`scripts/rank_precomputed_tfidf.py` reads the frozen Gutenberg tables
in `output/tfidf/` and prints the highest scoring terms.

```bash
python3 scripts/rank_precomputed_tfidf.py
python3 scripts/rank_precomputed_tfidf.py --top 12
python3 scripts/rank_precomputed_tfidf.py --only blake-poems.txt --only carroll-alice.txt
python3 scripts/rank_precomputed_tfidf.py --only shakespeare-macbeth.txt --min-length 4
```

`--min-length` drops short tokens after scores are loaded. It is a
viewer flag, not a change to the stored tables.

Lines whose second column is not a float are skipped. That is
deliberate: the 2012 dump has at least one garbled IDF-style value, and
the helper should still print a ranking.
