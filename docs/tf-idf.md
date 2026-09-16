# TF-IDF, as used in this toy corpus

This note is the math behind the original Perl scripts and the Python
example in `tfidf_toy/`. It is written so you can recompute every number
with a pencil, then check it against `python3 -m tfidf_toy demo`.

## Why weight terms at all?

A raw word count says “this token appears a lot.” That is rarely what you
want when you compare books. *The*, *and*, and *of* dominate every English
novel. What you usually want instead is:

> tokens that are **frequent in this document** and **rare in the rest of
> the collection**.

That product is **tf-idf** (term frequency × inverse document frequency).
In this repo it is a ranking score, not a probability.

## Term frequency (tf)

For document \(d\) and term \(t\):

\[
\mathrm{tf}(t, d) = \frac{\mathrm{count}(t, d)}{|d|}
\]

where \(|d|\) is the number of tokens in \(d\) after the tokenizer in
[`tokenization.md`](tokenization.md) has run.

This is **length-normalized** tf. A 3,000-word story and a 200,000-word
novel can be compared without the novel winning on every word simply
because it is longer.

The original Perl script (`tf-idf-values.pl`) writes one `output/tf/<file>`
table with this normalized value, not the raw count.

### What tf is not

- It is not BM25’s saturated tf.
- It is not log-tf (`1 + log count`).
- It does not discard stopwords. Words that appear in every document are
  handled by idf going to zero, not by a stoplist.

## Inverse document frequency (idf)

Let \(N\) be the number of documents in the collection, and
\(\mathrm{df}(t)\) the number of documents that contain \(t\) at least
once.

\[
\mathrm{idf}(t) = \ln \frac{N}{\mathrm{df}(t)}
\]

Natural log (`math.log` in Python, `log` in Perl). No smoothing, no
add-one, no \(N+1\).

Consequences:

| Situation | idf |
| --- | --- |
| \(t\) appears in every document | \(\ln(N/N) = 0\) |
| \(t\) appears in one document | \(\ln N\) (the maximum) |
| \(t\) appears in half the documents | \(\ln 2 \approx 0.693\) |

On this Gutenberg slice, \(N = 18\), so a one-document word has

\[
\ln 18 \approx 2.890371757896165
\]

That constant is exactly the idf stored in `output/idf.txt` for terms that
occur in a single file (for example `gryphon`, which only appears in
`carroll-alice.txt`).

### Smoothed idf (optional, Python only)

Collections with unseen query terms sometimes use

\[
\mathrm{idf}_{\mathrm{smooth}}(t) = \ln \frac{N + 1}{\mathrm{df}(t) + 1} + 1
\]

The Python CLI exposes this as `--idf smooth`. The original Perl run and
the committed `output/` tables use **raw** idf. Prefer raw when you want
to match this repo’s historical numbers.

## The product

\[
\mathrm{tfidf}(t, d) = \mathrm{tf}(t, d) \times \mathrm{idf}(t)
\]

If a word is common to every book, idf is 0, so tf-idf is 0 even if the
word occurs thousands of times. That is why `a`, `the`, `and`, and `about`
are stored as `0` in `output/tfidf/carroll-alice.txt`.

If a word is unique to one book and used often there, both factors are
large. `alice` in *Alice’s Adventures in Wonderland* is the extreme case
in this collection.

## Ranking, not comparing across formulas

Scores are comparable **within one collection, one tokenizer, one idf
variant**. They are not absolute “importance units.” Change \(N\), add a
book, or fold hyphens differently and every number moves.

Typical uses in this toy repo:

1. Sort a single document’s vocabulary by tf-idf and read the top 15
   tokens. Those are a cheap sketch of *what this text is about relative
   to the rest of the shelf*.
2. Compare two books by looking at terms with a large score in one and a
   near-zero score in the other (`python3 -m tfidf_toy compare ...`).

## Worked intuition on the real corpus

From the committed Perl output, the highest tf-idf tokens in
`carroll-alice.txt` include:

| token | why it ranks |
| --- | --- |
| `alice` | the protagonist’s name; almost collection-specific; very frequent |
| `gryphon`, `duchess`, `dormouse`, `hatter` | character names that barely appear elsewhere |
| `turtle` | “Mock Turtle”; repeated in one book |
| `rabbit`, `caterpillar` | distinctive but slightly more ordinary English words |

Words such as `herself` also surface: they are not “topic words,” but they
are *stylistically* denser in Carroll than in, say, the King James Bible.
tf-idf does not know about characters versus function words; it only knows
frequency contrast.

A longer reading of the 18-book shelf is in
[`gutenberg-results.md`](gutenberg-results.md).

## Formulas the scripts do not implement

Useful to know about, and easy to confuse with this toy:

| Name | Sketch | In this repo? |
| --- | --- | --- |
| Raw tf × idf | count × ln(N/df) | no (tf is normalized) |
| Log tf-idf | (1 + ln count) × idf | no |
| BM25 | saturated tf, document-length prior, usually smoothed idf | no |
| Sublinear Cosine tf-idf | often L2-normalized vectors for retrieval | no |
| sklearn `TfidfVectorizer` | several defaults (smooth idf, L2, stop words) | no |

The Python package is intentionally small so it stays inspectable next to
the Perl that produced `output/`.

## Next

- Token rules: [`tokenization.md`](tokenization.md)
- How the Perl files write `output/`: [`pipeline.md`](pipeline.md)
- Every arithmetic step on a 3-document corpus: [`worked-example.md`](worked-example.md)
