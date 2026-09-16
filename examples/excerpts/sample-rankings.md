# Sample rankings for the committed excerpts

Generated with:

```bash
python3 examples/python/tfidf_example.py \
  --input-dir examples/excerpts \
  --output-dir /tmp/excerpt-tfidf
```

`N = 3`, vocabulary = 349 terms. Token counts: Alice 313, Moby-Dick 221, Macbeth 168.

If you edit the `.txt` files, regenerate this page rather than treating the numbers as frozen API.

## alice-opening.txt — TF vs TF-IDF

TF:

```
   1   0.047923323  the
   2   0.038338658  it
   3   0.03514377   a
   4   0.03514377   to
   5   0.028753994  and
   6   0.028753994  she
   7   0.025559105  her
   8   0.025559105  of
```

TF-IDF:

```
   1   0.031589491  she
   2   0.028079547  her
   3   0.02105966   alice
   4   0.017549717  very
   5   0.014039774  down
   6   0.014039774  had
   7   0.014039774  rabbit
   8   0.01052983   suddenly
   9   0.0077724941 was
  10   0.0070198868 across
  11   0.0070198868 after
  12   0.0070198868 book
```

`she` has high TF **and** `df = 1` in this three-file shelf. `alice` is third, not first. That is the point of the excerpt example.

## moby-cetology.txt — TF-IDF

```
   1   0.029826578  whale
   2   0.019884385  sperm
   3   0.0099421927 are
   4   0.0099421927 books
   5   0.0099421927 both
   6   0.0099421927 complete
   7   0.0099421927 far
   8   0.0099421927 great
   9   0.0099421927 greenland
```

`whale` and `sperm` are repeated inside a short file and missing from the other two, so they behave like `cat` / `mat` in the tiny corpus.

## macbeth-witches.txt — TF-IDF

```
   1   0.019618077  1
   2   0.019618077  king
   3   0.013078718  2
   4   0.013078718  3
   5   0.013078718  bloody
   6   0.013078718  braue
   7   0.013078718  enter
   8   0.013078718  faire
   9   0.013078718  foule
  10   0.013078718  lightning
  11   0.013078718  macbeth
  12   0.013078718  meet
  13   0.013078718  three
  14   0.013078718  thunder
```

`1` / `2` / `3` are the Folio speech numbers (`1. When shall we three…`). `braue`, `faire`, `foule` are spelling. `macbeth`, `thunder`, and `lightning` are the content terms once you skip the numerals.
