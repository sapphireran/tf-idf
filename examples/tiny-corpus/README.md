# Tiny teaching corpus

Four one-sentence documents, 22-term vocabulary, every number small enough
to compute with a pencil. The Python script uses the same TF / IDF / TF-IDF
definitions as the Gutenberg snapshot (`tf = count / tokens`,
`idf = ln(N / df)`, `tfidf = tf * idf`) and a tokenizer aligned with the
Perl cleanup (lowercase, strip punctuation, split on spaces).

`N` is exactly 4 — the number of non-hidden files in `docs/`. That is the
behavior the Gutenberg Perl *meant* to have.

## Documents

| File | Text | Tokens |
| --- | --- | ---: |
| `docs/cats.txt` | Cats chase mice. Cats sleep on warm mats. | 8 |
| `docs/dogs.txt` | Dogs chase cats. Dogs sleep on warm porches. | 8 |
| `docs/space.txt` | Rockets fly past stars. Stars shine in deep space. | 9 |
| `docs/kitchen.txt` | Chefs chase warm bread. Bread smells in the kitchen. | 9 |

Shared verbs (`chase`) and adjectives (`warm`) are intentional: they show
IDF shrinking a term that three documents use. Unique nouns (`mice`,
`porches`, `rockets`, `bread`) keep `ln(4/1) ≈ 1.386`.

## Run

```bash
python3 examples/tiny-corpus/compute_tfidf.py
python3 examples/tiny-corpus/compute_tfidf.py --show-tokens
python3 examples/tiny-corpus/compute_tfidf.py --json
python3 examples/tiny-corpus/test_compute_tfidf.py
```

The test reimports `compute_tfidf.py` and checks the hand-calc values in
[expected-hand-calc.md](expected-hand-calc.md) to six decimal places.

## What to notice

1. In `cats.txt`, `cats` (tf 0.25, df 2) ties `mice` and `mats` (tf 0.125,
   df 1). Double the frequency, half the rarity.
2. In `dogs.txt`, `dogs` has no other document to share DF with, so the same
   0.25 TF becomes the largest score in the whole toy collection
   (`0.346574`).
3. `chase` appears in three of four files. It never ranks near the top,
   even though it is the only verb the cats, dogs, and chefs have in
   common.
4. `the` is *not* a collection-wide stopword here. It appears only in
   `kitchen.txt`, so it gets the maximum IDF. That is a reminder that
   stopword behavior is a property of the collection, not of the word.
