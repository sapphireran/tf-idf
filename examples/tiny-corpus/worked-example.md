# Worked example (every weight)

Same formulas as the Gutenberg toy:

\[
\mathrm{tf}(t, d)=\frac{\mathrm{count}(t,d)}{|d|}
\qquad
\mathrm{idf}(t)=\ln\frac{N}{\mathrm{df}(t)}
\qquad
\mathrm{tfidf}(t,d)=\mathrm{tf}(t,d)\times\mathrm{idf}(t)
\]

\(N=4\). Each note has \(|d|=9\) tokens after lowercase + punctuation strip. \(\ln\) is the natural log: \(\ln 2 \approx 0.69314718056\), \(\ln 4 = 2\ln 2 \approx 1.38629436112\).

## Tokens

| Document | Tokens |
| --- | --- |
| morning bakery | `the baker scored the bread and the bread cracked` |
| ridge trail | `the hiker followed the trail and the trail climbed` |
| afternoon bakery | `the baker heated the oven and the bread rose` |
| rehearsal room | `the singer followed the song and the song rose` |

## Term frequency

Every note is nine tokens, so a count of 1 is \(1/9\), a count of 2 is \(2/9\), a count of 3 is \(1/3\).

**Morning bakery**

| token | count | tf |
| --- | ---: | ---: |
| `the` | 3 | \(3/9\) |
| `bread` | 2 | \(2/9\) |
| `baker` | 1 | \(1/9\) |
| `scored` | 1 | \(1/9\) |
| `and` | 1 | \(1/9\) |
| `cracked` | 1 | \(1/9\) |

**Ridge trail**

| token | count | tf |
| --- | ---: | ---: |
| `the` | 3 | \(3/9\) |
| `trail` | 2 | \(2/9\) |
| `hiker` | 1 | \(1/9\) |
| `followed` | 1 | \(1/9\) |
| `and` | 1 | \(1/9\) |
| `climbed` | 1 | \(1/9\) |

**Afternoon bakery**

| token | count | tf |
| --- | ---: | ---: |
| `the` | 3 | \(3/9\) |
| `baker` | 1 | \(1/9\) |
| `heated` | 1 | \(1/9\) |
| `oven` | 1 | \(1/9\) |
| `and` | 1 | \(1/9\) |
| `bread` | 1 | \(1/9\) |
| `rose` | 1 | \(1/9\) |

**Rehearsal room**

| token | count | tf |
| --- | ---: | ---: |
| `the` | 3 | \(3/9\) |
| `song` | 2 | \(2/9\) |
| `singer` | 1 | \(1/9\) |
| `followed` | 1 | \(1/9\) |
| `and` | 1 | \(1/9\) |
| `rose` | 1 | \(1/9\) |

## Document frequency and IDF

\(\mathrm{df}(t)\) is “how many of the four notes contain \(t\) at least once”, not how many times it is written.

| token | df | idf | note |
| --- | ---: | --- | --- |
| `the` | 4 | \(\ln(4/4)=0\) | collection-wide; drops out |
| `and` | 4 | \(0\) | same |
| `baker` | 2 | \(\ln 2\) | both bakery notes |
| `bread` | 2 | \(\ln 2\) | both bakery notes |
| `followed` | 2 | \(\ln 2\) | trail + rehearsal |
| `rose` | 2 | \(\ln 2\) | afternoon + rehearsal |
| `scored` | 1 | \(\ln 4\) | morning only |
| `cracked` | 1 | \(\ln 4\) | morning only |
| `hiker` | 1 | \(\ln 4\) | trail only |
| `trail` | 1 | \(\ln 4\) | trail only |
| `climbed` | 1 | \(\ln 4\) | trail only |
| `heated` | 1 | \(\ln 4\) | afternoon only |
| `oven` | 1 | \(\ln 4\) | afternoon only |
| `singer` | 1 | \(\ln 4\) | rehearsal only |
| `song` | 1 | \(\ln 4\) | rehearsal only |

## `tf * idf` per note

Zeros for `the` and `and` are omitted below; they are present in every file the scripts write.

Useful building blocks:

\[
\frac{1}{9}\ln 2 \approx 0.07701635340
\qquad
\frac{2}{9}\ln 2 \approx 0.15403270679
\qquad
\frac{1}{9}\ln 4 \approx 0.15403270679
\qquad
\frac{2}{9}\ln 4 \approx 0.30806541358
\]

Notice \(\frac{2}{9}\ln 2 = \frac{1}{9}\ln 4\). A double mention of a two-document word ties a single mention of a one-document word.

**Morning bakery**

| token | tf × idf | arithmetic |
| --- | ---: | --- |
| `bread` | 0.154033 | \((2/9)\ln 2\) |
| `cracked` | 0.154033 | \((1/9)\ln 4\) |
| `scored` | 0.154033 | \((1/9)\ln 4\) |
| `baker` | 0.077016 | \((1/9)\ln 2\) |

`bread` is not “more important” than `scored` here. It is mentioned twice but is only half as rare.

**Ridge trail**

| token | tf × idf | arithmetic |
| --- | ---: | --- |
| `trail` | 0.308065 | \((2/9)\ln 4\) |
| `climbed` | 0.154033 | \((1/9)\ln 4\) |
| `hiker` | 0.154033 | \((1/9)\ln 4\) |
| `followed` | 0.077016 | \((1/9)\ln 2\) |

**Afternoon bakery**

| token | tf × idf | arithmetic |
| --- | ---: | --- |
| `heated` | 0.154033 | \((1/9)\ln 4\) |
| `oven` | 0.154033 | \((1/9)\ln 4\) |
| `baker` | 0.077016 | \((1/9)\ln 2\) |
| `bread` | 0.077016 | \((1/9)\ln 2\) |
| `rose` | 0.077016 | \((1/9)\ln 2\) |

**Rehearsal room**

| token | tf × idf | arithmetic |
| --- | ---: | --- |
| `song` | 0.308065 | \((2/9)\ln 4\) |
| `singer` | 0.154033 | \((1/9)\ln 4\) |
| `followed` | 0.077016 | \((1/9)\ln 2\) |
| `rose` | 0.077016 | \((1/9)\ln 2\) |

## Cosine similarity

Only tokens with a nonzero weight in **both** notes contribute to the dot product. `the` and `and` never do.

| pair | shared weighted tokens | cosine |
| --- | --- | ---: |
| morning bakery ↔ afternoon bakery | `baker`, `bread` | 0.250873 |
| afternoon bakery ↔ rehearsal | `rose` | 0.064282 |
| ridge trail ↔ rehearsal | `followed` | 0.042640 |
| morning bakery ↔ ridge trail | — | 0 |
| morning bakery ↔ rehearsal | — | 0 |
| ridge trail ↔ afternoon bakery | — | 0 |

The two bakery notes are the only pair that share *two* content tokens, and they win. Sharing a single mid-idf verb (`rose` or `followed`) is a weak link. Sharing only `the` / `and` is no link at all.

Dot product for the bakery pair, if you want to recompute the cosine:

\[
\mathbf{v}_1\cdot\mathbf{v}_3
= \Bigl(\tfrac19\ln 2\Bigr)^2 + \Bigl(\tfrac29\ln 2\Bigr)\Bigl(\tfrac19\ln 2\Bigr)
= 3\Bigl(\tfrac19\ln 2\Bigr)^2
\approx 0.01779455607
\]

\[
\|\mathbf{v}_1\| \approx 0.27768641122
\qquad
\|\mathbf{v}_3\| \approx 0.25543434693
\qquad
\cos = \frac{0.01779455607}{0.27768641122\times 0.25543434693} \approx 0.25087260300
\]

## What this is illustrating

1. Collection-wide tokens get idf 0. That is the implicit stoplist.
2. A token mentioned twice can tie a rarer token mentioned once (\(\frac{2}{9}\ln 2 = \frac{1}{9}\ln 4\)).
3. Cosine cares about *overlap of weighted dimensions*, not about both notes containing `the`.
4. `rose` matching across a loaf and a melody is the sense-collision you also get with Gutenberg `lord` or `o`.

Regenerate the machine-readable copy of these tables with `tfidf_toy.py` (see this directory's README) and compare [`expected-results.md`](expected-results.md).
