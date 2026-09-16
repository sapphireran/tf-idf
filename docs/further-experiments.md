# Further experiments (personal)

Things to try that stay inside this repository. None of these need a search cluster.

## 1. Copy Alice and watch IDF fall

```bash
cp gutenberg/carroll-alice.txt gutenberg/carroll-alice-copy.txt
python3 examples/python/tfidf_example.py \
  --input-dir gutenberg \
  --output-dir /tmp/alice-copy-run
grep -w '^alice' /tmp/alice-copy-run/idf.txt output/idf.txt
rm gutenberg/carroll-alice-copy.txt
```

Committed `idf(alice) = ln(18/3) ≈ 1.792`. After the copy, `df = 4` and `N = 19`, so `ln(19/4) ≈ 1.558`. The TF-IDF of `alice` in the original file drops by the same ratio. `gryphon` barely moves if the copy is identical (its DF also +1).

## 2. Split the King James file by testament

The whole KJV is one document, so `david` and `jesus` share a DF of 1. Cut the file at the Matthew heading into `ot.txt` and `nt.txt`, rerun on a folder that contains those two plus the novels. Biblical names that are testament-specific keep high IDF; `unto` / `thee` / `lord` fall because they appear in both halves *and* in Milton / Shakespeare.

## 3. Drop the speech prefixes

Before running the Python example on `gutenberg/shakespeare-*.txt`, delete tokens that match `^(ham|hor|qu|laer|ophe|pol|macb|macd|rosse|bru|cassi|caes)$`. Hamlet's ranking should start at `horatio` / `hamlet` instead of `ham`. This is the cleanup [interpreting-results.md](interpreting-results.md) asks for.

## 4. Compare raw IDF to smooth IDF

In `tfidf_example.py`, replace

```python
idf[term] = math.log(n / df)
```

with

```python
idf[term] = math.log((n + 1) / (df + 1)) + 1
```

Rerun the tiny corpus. `the` is no longer 0; `cat` is no longer `ln(3)/6`. The Gutenberg Alice list will still put `alice` first, but `the` will re-enter the long tail with a small positive score. That is the variant most library tutorials mean by "smoothed IDF".

## 5. Cosine between books

After a Gutenberg run into `/tmp/gutenberg-tfidf`, treat each `tfidf/*.txt` as a sparse vector and compute cosine(`emma`, `persuasion`) vs cosine(`emma`, `moby_dick`). Austen should be closer to Austen. You will want to drop exact-zero coordinates or they do nothing anyway. This repo does not L2-normalize for you.

## 6. Tiny corpus with unequal lengths

Replace `docs/cats.txt` with a 30-word paragraph that says `cat` once. `tf(cat)` falls from 1/6 to 1/30 and cats.txt stops looking like "a cat document" even though DF is unchanged. That is why the Perl script divides by `word_count`.

## 7. Quote the star

```bash
perl 'tf*idf-product.pl'
```

If you have already rebuilt `output/tf/` and `output/idf.txt`, this is the only second step. Unquoted, the shell globs. See [known-quirks.md](known-quirks.md).

## 8. Count zeros

```bash
python3 examples/python/extract_top_terms.py --zeros output/tfidf/carroll-alice.txt
python3 examples/python/extract_top_terms.py --zeros output/tfidf/bible-kjv.txt
```

The KJV has more terms, but both files have a block of function words at exactly 0. The size of that block is "how much of this book's vocabulary is collection-wide."
