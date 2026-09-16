# TF-IDF math used in this repo

This note is the worked-out version of the scoring used by the two Perl
scripts. It is written so you can reproduce every number with a pencil,
then check the same numbers with `examples/mini_tfidf.py`.

The formula is the textbook product

\[
\mathrm{tfidf}(t, d) = \mathrm{tf}(t, d) \times \mathrm{idf}(t)
\]

where \(t\) is a term (a token) and \(d\) is a document. Nothing else is
smoothed, logged, or length-normalized beyond the TF definition below.

## Term frequency

After tokenization (see [perl-pipeline.md](perl-pipeline.md)), each
document is a bag of tokens. Let \(n_{t,d}\) be the raw count of term
\(t\) in document \(d\), and let \(|d|\) be the total number of tokens
in \(d\), including repeats.

\[
\mathrm{tf}(t, d) = \frac{n_{t,d}}{|d|}
\]

This is **L1-normalized TF**: every document's TF values sum to 1. A
word that appears twice in a 10-token document scores `0.2`, the same as
a word that appears 200 times in a 1,000-token document. Long books
therefore do not automatically outrank short poems.

The scripts write one `word<TAB>tf` line per distinct token, alphabetically,
under `output/tf/<filename>`.

## Inverse document frequency

Let \(N\) be the number of documents in the collection, and let
\(\mathrm{df}(t)\) be the number of those documents that contain \(t\)
at least once.

\[
\mathrm{idf}(t) = \ln\frac{N}{\mathrm{df}(t)}
\]

The logarithm is the **natural log** (`log` in Perl, `math.log` in
Python). Base 10 or base 2 would only rescale every score by a constant;
rankings inside a single document would stay the same.

Important consequences:

| Situation | IDF | Meaning |
| --- | --- | --- |
| Term in every document | \(\ln(N/N) = 0\) | The term cannot distinguish documents. `the`, `a`, and `and` score exactly 0 in the committed Gutenberg tables. |
| Term in one document | \(\ln(N/1) = \ln N\) | Maximum rarity. For this corpus, \(\ln 18 \approx 2.89037175789616\). |
| Term in \(k\) documents | \(\ln(N/k)\) | Falls as \(k\) grows. |

The committed `output/idf.txt` was generated with **\(N = 18\)**, the
number of `.txt` books, not the number of directory entries. See
[quirks-and-variants.md](quirks-and-variants.md) for the off-by-dot
history.

## The product

`tf*idf-product.pl` multiplies the two columns. A high score needs
**both** ingredients:

1. The term is common *inside* this document (high TF).
2. The term is rare *across* the collection (high IDF).

A character name that appears hundreds of times in one novel and almost
nowhere else is the textbook case. A function word that appears
everywhere is wiped out by IDF, even if its TF is huge.

## Three-document walkthrough

The files in `examples/mini_corpus/three_docs/` are:

| File | Text |
| --- | --- |
| `the_harbor.txt` | `the whale swims in the harbor` |
| `the_song.txt` | `the whale sings a song` |
| `the_bird.txt` | `the bird sings a song` |

Token counts: harbor document \(= 6\), song document \(= 5\), bird
document \(= 5\). Collection size \(N = 3\).

### Document frequency

| Term | Documents | \(\mathrm{df}\) | \(\mathrm{idf} = \ln(3/\mathrm{df})\) |
| --- | ---: | ---: | ---: |
| `the` | all three | 3 | \(\ln 1 = 0\) |
| `a` | song, bird | 2 | \(\ln(3/2) \approx 0.4054651081081644\) |
| `whale` | harbor, song | 2 | \(\approx 0.4054651081081644\) |
| `sings` | song, bird | 2 | \(\approx 0.4054651081081644\) |
| `song` | song, bird | 2 | \(\approx 0.4054651081081644\) |
| `swims` | harbor | 1 | \(\ln 3 \approx 1.0986122886681098\) |
| `in` | harbor | 1 | \(\approx 1.0986122886681098\) |
| `harbor` | harbor | 1 | \(\approx 1.0986122886681098\) |
| `bird` | bird | 1 | \(\approx 1.0986122886681098\) |

### Harbor document

| Term | Raw count | TF | TF-IDF |
| --- | ---: | ---: | ---: |
| `the` | 2 | \(2/6 \approx 0.333333\) | \(0.333333 \times 0 = 0\) |
| `whale` | 1 | \(1/6 \approx 0.166667\) | \(\approx 0.067578\) |
| `swims` | 1 | \(1/6\) | \(\approx 0.183102\) |
| `in` | 1 | \(1/6\) | \(\approx 0.183102\) |
| `harbor` | 1 | \(1/6\) | \(\approx 0.183102\) |

`the` is the most frequent token and still scores zero. The three
document-specific words tie for first.

### Song document

Every content word appears once in a five-token document, so each has
TF \(= 0.2\). `the` is again zero. The remaining four terms
(`whale`, `sings`, `a`, `song`) all score

\[
0.2 \times \ln(3/2) \approx 0.081093
\]

### Bird document

Same shape as the song document, except `bird` is unique:

\[
\mathrm{tfidf}(\texttt{bird}) = 0.2 \times \ln 3 \approx 0.219722
\]

That is the highest score in the toy collection. Rarity plus a short
document is a strong combination.

## What the score is not

TF-IDF as implemented here is **not**:

- a probability
- comparable across documents as an absolute "importance units" scale
  (a short children's story can produce larger raw products than *Moby
  Dick* because \(|d|\) is in the denominator)
- a semantic embedding (there is no notion of synonymy; `whale` and
  `whales` are different terms)
- BM25, which adds term-frequency saturation and document-length
  normalization

Use it as a **within-document ranking** of which tokens are most
characteristic of that text relative to the rest of *this* collection.

## Alice, one real number

From the committed Gutenberg run:

| Quantity | Value | Source |
| --- | --- | --- |
| \(\mathrm{tf}(\texttt{alice}, \textit{Alice})\) | `0.0144867549668874` | `output/tf/carroll-alice.txt` |
| \(\mathrm{df}(\texttt{alice})\) | 3 | `output/df.txt` (Carroll, Chesterton *Thursday*, Edgeworth) |
| \(\mathrm{idf}(\texttt{alice})\) | `1.79175946922805` \(= \ln(18/3)\) | `output/idf.txt` |
| product | `0.025956780390307` | `output/tfidf/carroll-alice.txt` |

Check: \(0.0144867549668874 \times 1.79175946922805 \approx 0.02595678\).

`the` in the same book has TF `0.0612959060806743` — more than four
times Alice's TF — and TF-IDF `0`, because \(\mathrm{df}(\texttt{the}) =
18\).

For the full Alice walkthrough, see
[../examples/walkthroughs/alice_through_the_pipeline.md](../examples/walkthroughs/alice_through_the_pipeline.md).
