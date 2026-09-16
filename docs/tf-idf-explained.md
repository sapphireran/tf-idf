# What tf-idf measures in this repo

tf-idf is a **ranking heuristic**, not a linguistic theory. It answers one question:

> Which words are unusually concentrated in *this* document, relative to the rest of *this* collection?

Change the collection and the scores change. `whale` is distinctive in *Moby-Dick* among these 18 files. In a collection of only whaling logs it would not be.

## The three pieces

### Term frequency (tf)

Raw count \(\mathrm{count}(t, d)\) favors long books. The Perl pipeline and the tiny-corpus example both use the **length-normalized** share:

\[
\mathrm{tf}(t, d) = \frac{\mathrm{count}(t, d)}{\sum_{t'} \mathrm{count}(t', d)}
\]

The denominator is the number of tokens after the same cleanup rules (lowercase, strip non-alphanumerics, split on spaces). Empty tokens are not counted in the Python example; the original Perl increments a counter for every split field, including empties created by double spaces, then skips those empties when filling the `%tf` hash. On the Gutenberg dump the difference is negligible. On a hand-built example you should count tokens the same way the script you are checking does.

Properties:

- Every document’s tf values sum to about \(1\) (exactly \(1\) if empty tokens are excluded).
- A word that appears twice in a 5-token document has \(\mathrm{tf} = 0.4\).
- A word that appears twice in a 10,000-token document has \(\mathrm{tf} = 0.0002\).

### Document frequency (df)

\[
\mathrm{df}(t) = \bigl|\{ d : \mathrm{count}(t, d) > 0 \}\bigr|
\]

One occurrence is enough. *Moby-Dick* mentioning `nantucket` 50 times and Blake mentioning it once still gives those two files a contribution of \(1\) each.

`output/df.txt` also lists the filenames, which is the right place to debug a surprising idf.

### Inverse document frequency (idf)

The scripts use **natural log** and **no smoothing**:

\[
\mathrm{idf}(t) = \ln\frac{N}{\mathrm{df}(t)}
\]

| Situation | \(\mathrm{df}\) | \(\mathrm{idf}\) |
| --- | ---: | --- |
| Term in one document only | \(1\) | \(\ln N\) |
| Term in half the collection | \(N/2\) | \(\ln 2 \approx 0.693\) |
| Term in every document | \(N\) | \(0\) |

That last row is why `the`, `and`, and `to` drop out of the Gutenberg rankings when they really do appear in all 18 files. A displayed score of `0` usually means “collection-wide,” not “missing.”

Division by zero cannot happen: a term is only in the idf table if it occurred at least once, so \(\mathrm{df} \ge 1\).

See [idf-variants.md](idf-variants.md) for `ln((N+1)/(df+1))`, probabilistic idf, and why search engines add smoothing.

## The product

\[
\mathrm{tfidf}(t, d) = \mathrm{tf}(t, d) \cdot \mathrm{idf}(t)
\]

Two ways to get a small score:

1. The word is rare *inside* the document (small tf), even if it is rare in the collection too.
2. The word is common *across* the collection (small idf), even if this document uses it constantly.

Two ways to get a large score:

1. High tf and high idf: a rare name used often (`alice`, `ahab`, `emma`).
2. Moderate tf and very high idf: a nonce word that appears a handful of times in one short file (`gryphon`, `thel`).

A short file can therefore outrank a long file for a unique word. That is intended.

## What the score is not

- **Not a probability.** Values are not between \(0\) and \(1\) for a fixed reason, and they do not sum to \(1\) across a document (idf weights break that).
- **Not a keyword extractor with a stopword list.** Function words vanish only when \(\mathrm{df} = N\). In a two-document collection, `the` can still win.
- **Not robust to tokenization.** `Alice's` → `alices`. `I'm` → `im`. Shakespeare `haue` never merges with `have`.
- **Not robust to morphology.** `whale` and `whales` are two terms. Both can rank, which is a feature when you are learning and a nuisance when you want one topic label.
- **Not a comparison across collections.** Do not compare an Alice score from this repo to an Alice score computed on a 10,000-book crawl.
- **Not BM25.** There is no document-length parameter \(b\), no term-frequency saturation \(k_1\), and no query. This is the 1970s textbook product, which is the point.

## A picture of the ranking

Imagine each term as a point:

- x-axis: how concentrated it is in one book (tf).
- y-axis: how unusual it is in the collection (idf).

tf-idf is a rectangular area. Names of people, places, and invented creatures sit up and to the right. Function words sit on the x-axis (`idf = 0`) or very close to it.

When you sort `output/tfidf/carroll-alice.txt` you are reading that area, largest first.

## Worked numbers

A three-document calculation with every intermediate value is in [examples/hand-calculation.md](../examples/hand-calculation.md). A five-document original corpus you can rerun is in [examples/tiny-corpus/](../examples/tiny-corpus/).

Those two examples are the right place to argue about a formula. The Gutenberg `output/` tree is the right place to argue about *interpretation* (speaker tags, old spelling, header years). That split is deliberate.

## Matching this repo vs. “the tf-idf you saw in a tutorial”

| Choice | This repo | Common tutorial variant |
| --- | --- | --- |
| Log base | Natural (`ln`) | \(\log_{10}\) or \(\log_2\) |
| Smoothing | None | \(\ln(N / \mathrm{df}) + 1\) or \(\ln((N+1)/(\mathrm{df}+1))+1\) |
| tf | Raw count / tokens | Often \(1 + \ln(\mathrm{count})\) or BM25 tf |
| Stopwords | Implicit via \(\mathrm{idf}=0\) | Explicit list |
| Vector use | Per-term tables only | Cosine similarity between documents |

If you port the idea to another language, match the first two columns before you compare floats to `output/idf.txt`.
