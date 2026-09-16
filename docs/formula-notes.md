# Formula notes

The product this repo teaches is:

```
tf(t, d)    = count(t, d) / tokens(d)
idf(t)      = ln( N / df(t) )
tfidf(t, d) = tf(t, d) * idf(t)
```

That matches the committed `output/` files when `N` is the number of
texts (18). Other tools will print different numbers for the same
corpus. This page lists the usual knobs.

## Document count `N`

Count the documents you tokenized.

The historical script uses `$#files` after `readdir`, which is larger
than 18 as soon as `.` / `..` / `.DS_Store` are in the listing. See
[perl-pipeline.md](perl-pipeline.md). The Python and cleaned Perl
examples take `N = len(processed_files)`.

`--faithful-perl` in `examples/python/tfidf.py` only reproduces the
empty-token denominator. It still uses a real document count, because
reproducing `$#files` would depend on whatever extra directory entries
happen to exist on disk.

## Logarithm base

| Base | Who uses it | Effect |
| --- | --- | --- |
| `ln` (natural) | Perl `log`, Python `math.log`, this repo | Numbers in `output/idf.txt` |
| `log10` | some IR textbooks | All idf values scale by `1 / ln(10)` |
| `log2` | some search notes | Scale by `1 / ln(2)` |

Changing base multiplies every idf (and every tf-idf) by a constant.
**Ranking inside one document does not change.** Absolute values do.

## Zero and smoothing

Raw `ln(N / df)` is 0 when `df = N`, and undefined if `df = 0`.
`df = 0` cannot happen for a term you actually observed. It can happen
if you apply a vocabulary from another collection.

Common smoothers:

```
idf_smooth     = ln( N / (1 + df) ) + 1          # never zero
idf_sklearn    = ln( (N + 1) / (df + 1) ) + 1    # TfidfVectorizer default
idf_prob       = ln( (N - df) / df )             # probabilistic idf
```

sklearn then L2-normalizes each document row. That is why a
`TfidfVectorizer` dump will not match `output/tfidf/carroll-alice.txt`
even if you disable stopwords.

The example CLI can emit the raw formula (default) or the sklearn-style
idf without L2:

```bash
python3 examples/python/tfidf.py \
  --input examples/tiny-corpus \
  --idf raw \
  --top 5

python3 examples/python/tfidf.py \
  --input examples/tiny-corpus \
  --idf sklearn \
  --top 5
```

On the tiny corpus, raw idf sends `the` to 0. The sklearn-style idf
does not, so `the` stays in the table with a small but nonzero score.

## Term frequency variants

| Name | Definition | Bias |
| --- | --- | --- |
| raw | `count` | long documents |
| normalized (this repo) | `count / tokens` | none from length |
| boolean | `1` if count > 0 | ignores repeats |
| sublinear | `1 + ln(count)` if count > 0 | dampens “alice alice alice” |

Normalized tf is the right default for this Gutenberg slice because the
KJV is an order of magnitude longer than Blake.

## Cosine similarity (not implemented)

If you want “documents like this one”, treat each file's tf-idf map as
a sparse vector and compute:

```
cos(a, b) = (a · b) / (||a|| ||b||)
```

Terms with `idf = 0` contribute nothing to the dot product. You do not
need an extra stoplist for that to work on this collection. The example
library exposes `cosine_similarity()` so the themes corpus can show
that bakery is closer to itself than to the observatory file.

## Floating point

Perl and Python both use IEEE-754 doubles for these logs. The tiny
corpus tests compare against values stored in
`examples/tiny-corpus/expected.json` with a `1e-12` absolute tolerance.
The committed Gutenberg tables were written by Perl's default string
rounding; recomputing in Python will differ in the last digits and is
not checked in CI.
