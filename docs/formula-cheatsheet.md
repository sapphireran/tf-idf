# Formula cheat sheet

Symbols match the 2012 Perl toy and `examples/tfidf_toy.py`.

## Cleaning

1. Lowercase.
2. Replace runs of whitespace with a single space.
3. Delete characters that are not `[a-z0-9]` or whitespace.
4. Split on spaces; drop empty strings.

Each surviving string is a **term**. The list of terms in a file is
the **document**. `|d|` is `len(tokens)`, not the number of unique
terms.

## Term frequency (length-normalized)

\[
\mathrm{tf}(t,d)=\frac{\mathrm{count}(t,d)}{|d|}
\]

Raw counts are **not** used as TF in this repo.

## Document frequency

\[
\mathrm{df}(t)=\bigl|\{d : \mathrm{count}(t,d)>0\}\bigr|
\]

Presence, not sum of counts. A word used 400 times in one book and
never elsewhere still has `df = 1`.

## Inverse document frequency (unsmoothed)

\[
\mathrm{idf}(t)=\ln\frac{N}{\mathrm{df}(t)}
\]

- `ln` is the natural logarithm (`log` in Perl, `math.log` in Python).
- `N` is the number of documents that were tokenized.
- No `+1` anywhere. If `df(t) = N`, then `idf(t) = 0`.

Useful constants for the corpora in this tree:

| corpus | N | max idf = ln(N) | idf of a term in half the docs |
| --- | ---: | ---: | ---: |
| classic three docs | 3 | 1.098612 | ln(3/2) ≈ 0.405465 if df = 2, not half |
| tiny five vignettes | 5 | 1.609438 | ln(5/2) ≈ 0.916291 |
| Gutenberg snapshot | 18 | 2.890372 | ln(18/9) = ln(2) ≈ 0.693147 |

## Product

\[
\mathrm{tfidf}(t,d)=\mathrm{tf}(t,d)\cdot\mathrm{idf}(t)
\]

Missing IDF (should not happen if both tables come from one run) is
treated as 0 in the Python toy.

## Ranking

Sort by `tfidf` descending. Break remaining ties with the term string
ascending so the output is stable.

## Variants this toy does not use

| name | formula | why people use it |
| --- | --- | --- |
| raw TF | `count(t,d)` | simpler; long docs dominate |
| log TF | `1 + ln(count)` if count > 0 | dampen very frequent terms |
| smoothed IDF | `ln(N / (df + 1)) + 1` | avoid zeros, avoid div-by-zero on unseen terms |
| BM25 | saturated TF plus length prior | ranking documents against a query |

Those are good follow-on experiments for `examples/tiny-corpus/`.
They would no longer match `output/tfidf/`.
