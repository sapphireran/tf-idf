# Formula variants

This toy uses one specific product. Other systems that also say “tf-idf” will not reproduce `output/tfidf/`. The differences are small on a chalkboard and large in a ranking.

All logarithms below are natural logs, matching Perl’s `log` and Python’s `math.log`.

## What this repository computes

Let \(c(t,d)\) be the raw count, \(n_d\) the token denominator for document \(d\), \(N\) the collection size, and \(\mathrm{df}(t)\) the number of documents that contain \(t\).

```text
tf(t, d)    = c(t, d) / n_d
idf(t)      = ln( N / df(t) )
tfidf(t, d) = tf(t, d) * idf(t)
```

No smoothing, no log tf, no extra `+ 1` on idf, no cosine at write time. A term that appears in every document gets idf 0 and disappears.

`examples/tfidf_mini.py` implements exactly this, with \(N\) equal to the number of files parsed.

## Common variants you will hit in libraries

| Name | tf | idf | Notes |
| --- | --- | --- | --- |
| **this repo** | \(c / n_d\) | \(\ln(N / \mathrm{df})\) | Teaching default |
| **log tf** | \(1 + \ln c\) if \(c>0\) else 0 | same idf | Dampens “whale” vs “ahab” |
| **smooth idf** | any | \(\ln((N+1)/(\mathrm{df}+1)) + 1\) | Never zero; stopwords survive |
| **sklearn `TfidfTransformer` default** | raw or l2-normalized counts | \(\ln((N+1)/(\mathrm{df}+1)) + 1\), then **l2** | `smooth_idf=True`, `norm='l2'` |
| **Okapi BM25** | saturated tf \(\frac{c(k_1+1)}{c + k_1(1-b+b\cdot n_d/\bar n)}\) | \(\ln\frac{N-\mathrm{df}+0.5}{\mathrm{df}+0.5}\) | A ranking function, not a vector |

sklearn’s extra `+ 1` on idf is why `the` would **not** go to zero even if it occurred in every document. This repo’s tables make the opposite pedagogical choice on purpose.

Log tf would pull *Moby-Dick*’s `whale` (very high count) closer to `ahab`. The committed ranking has whale just above ahab; a log tf would likely reverse or shrink that gap. That is a modeling decision, not a bug in either formula.

## Cosine is a *use* of the vector, not a different tf-idf

Once each document is a sparse vector of tf-idf weights, similarity is usually

\[
\cos(u, v) = \frac{u \cdot v}{\lvert u \rvert \lvert v \rvert}
\]

Zeros do not contribute. `the` can sit in the table at 0 and the cosine ignores it.

```bash
python3 examples/cosine_similarity.py --toy
python3 examples/cosine_similarity.py --matrix --n 12
python3 examples/cosine_similarity.py \
    output/tfidf/austen-emma.txt output/tfidf/austen-sense.txt
```

On the toy corpus, `cats.txt` is close to `pets.txt` and almost orthogonal to `space.txt`.

On the Gutenberg snapshot the geometry is *not* a clean author-clustering demo. `examples/cosine_similarity.py --matrix` on the committed tables puts Shakespeare plays at the top **because they share old spelling** (`haue`, `vpon`, `vs`), then Milton/Blake/Whitman/KJV **because they share** `thee` / `thou` / `hath` / `thy`. Austen novels sit in a looser band with Edgeworth (`mr`, `mrs`, `have`, `herself`). Chesterton’s three books do *not* form a tight triangle: each vector is dominated by unique proper names (`syme`, `macian`, Father Brown’s cases), so the leftover overlap is generic.

That is still useful. It shows cosine inheriting every tokenizer and collection-design choice that went into the weights. Details and captured stdout: [`../examples/reading-sample-sessions.md`](../examples/reading-sample-sessions.md).

## What not to mix

- Do not compare a sklearn l2-normalized vector to a row of `output/tfidf/` and expect the same top term.
- Do not mix log tf in one document with raw tf in another.
- Do not change \(N\) (or the tokenizer) and keep quoting the floats in `docs/interpreting-results.md`.

If you experiment, keep the variant name next to the ranking. The helpers in `examples/` all implement **this repo’s** product unless the file name says otherwise.
