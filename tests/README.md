# Tests

Stdlib `unittest` only. From the repository root:

```bash
python3 tests/test_tfidf_toy.py
python3 tests/test_rank_precomputed.py
python3 -m unittest discover -s tests -v
```

`test_tfidf_toy.py` rebuilds TF-IDF for the tiny corpora on every run.
It checks the three-sentence hand example, the five-vignette headwords
(`soup`, `roses`, `boat`, `oak`, `hill`), and tokenizer rules.

`test_rank_precomputed.py` reads the frozen Gutenberg tables. It
asserts that *Alice* ranks `alice`, *Moby-Dick* ranks `whale` then
`ahab`, and Burgess's Buster Bear outscores Alice's head term. Those
are properties of the committed `output/` snapshot, not of a live
Perl rerun.
