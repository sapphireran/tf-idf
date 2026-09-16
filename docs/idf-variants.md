# IDF variants

This repo’s Perl scripts and the tiny-corpus helper default to **unsmoothed natural-log idf**:

\[
\mathrm{idf}_{\mathrm{raw}}(t) = \ln\frac{N}{\mathrm{df}(t)}
\]

That is the shortest formula that still does the job: rare terms get a large weight, collection-wide terms get zero. Search systems almost never ship this raw form. This page records the usual cousins so you can see what would change in the three-document hand example and in the Gutenberg snapshot.

The helper prints several columns when you pass `--variants`. It does not change the files it writes; those stay raw so they remain comparable to `output/idf.txt`.

## Why people change the formula

1. **Zero weights.** \(\mathrm{df} = N\) ⇒ \(\mathrm{idf} = 0\). A query term that appears in every document disappears from the score. Sometimes you want that (stopword-like behavior). Sometimes you still want a little weight.
2. **Unstable rare terms.** \(\mathrm{df} = 1\) ⇒ \(\mathrm{idf} = \ln N\). In a 10-million-document crawl that is a huge number, and a single OCR typo can outrank a real name. Smoothing and BM25-style saturation exist to calm that down.
3. **Negative idf.** Some “probabilistic” forms use \(\ln((N-\mathrm{df})/\mathrm{df})\). When \(\mathrm{df} > N/2\) the weight goes negative. Fine in a research paper; surprising in a teaching table.
4. **Log base.** \(\ln\), \(\log_{10}\), and \(\log_2\) are positive multiples of each other. Rankings of **the same formula family** do not change. Mixing bases while comparing floats to `output/idf.txt` does.

## Family 1: add-one / smoothed textbook

\[
\mathrm{idf}_{\mathrm{smooth}}(t) = \ln\frac{N}{\mathrm{df}(t)} + 1
\]

Every term keeps at least weight \(1\). Collection-wide words in Alice (`a`, `about`) would no longer print as `0`; they would print as their tf (because \(\mathrm{tf} \times 1 = \mathrm{tf}\)). Distinctive names still win, but the gap shrinks.

A common extra smooth on both counts:

\[
\mathrm{idf}_{\mathrm{add1}}(t) = \ln\frac{N+1}{\mathrm{df}(t)+1} + 1
\]

`+1` in the fraction avoids ever taking \(\ln\) of something awkward if you define idf for unseen query terms (\(\mathrm{df} = 0\)). This repo never scores unseen terms, so the extra `+1` is only a ranking tweak.

### Hand-example check (d3, term `tea` vs `and`)

From [examples/hand-calculation.md](../examples/hand-calculation.md): \(N=3\), \(\mathrm{df}(\mathtt{tea})=2\), \(\mathrm{df}(\mathtt{and})=1\), \(\mathrm{tf}(\mathtt{tea})=0.4\), \(\mathrm{tf}(\mathtt{and})=0.2\).

| variant | tea | and | winner |
| --- | ---: | ---: | --- |
| raw \(\ln(N/\mathrm{df})\) | \(0.4 \times \ln 1.5 \approx 0.162\) | \(0.2 \times \ln 3 \approx 0.220\) | **and** |
| smooth \(+1\) | \(0.4 \times (\ln 1.5+1) \approx 0.562\) | \(0.2 \times (\ln 3+1) \approx 0.420\) | **tea** |
| add1 \(+1\) | \(0.4 \times (\ln(4/3)+1) \approx 0.515\) | \(0.2 \times (\ln(4/2)+1) \approx 0.339\) | **tea** |

Smoothing is enough to let the repeated topic word beat the unique stopword. That is the usual reason tutorials add `+1`.

## Family 2: probabilistic / Robertson–Sparck Jones flavor

\[
\mathrm{idf}_{\mathrm{prob}}(t) = \ln\frac{N - \mathrm{df}(t)}{\mathrm{df}(t)}
\]

| df | \(N=3\) | weight |
| ---: | --- | ---: |
| 1 | \(\ln(2/1)\) | `0.6931471806` |
| 2 | \(\ln(1/2)\) | **negative** `-0.6931471806` |

Terms in more than half the collection actively *subtract*. d3’s `tea` (\(\mathrm{df}=2\)) would drag the score down. Teaching tables become hard to read; skip this form unless you are reproducing a specific IR paper.

A guarded version uses \(\max(0, \cdot)\) so the weight floors at zero instead of going negative.

## Family 3: BM25 idf (as commonly implemented)

Okapi BM25’s idf, in the form Lucene used for a long time:

\[
\mathrm{idf}_{\mathrm{BM25}}(t) = \ln\frac{N - \mathrm{df}(t) + 0.5}{\mathrm{df}(t) + 0.5}
\]

Still can be negative when df is large. Elasticsearch later documented a `+1` floor variant. BM25 *also* replaces raw tf with a saturated function of count and document length. Porting only this idf piece onto the Perl pipeline is not BM25.

This repo does not implement BM25. The `--variants` column is there so you can see the idf factor move, not so you can claim BM25 scores.

## Family 4: change tf instead of idf

Two popular tf substitutes, neither used by the Perl scripts:

\[
\mathrm{tf}_{\log}(t, d) = 1 + \ln(\mathrm{count}(t, d))
\quad \text{when count} > 0
\]

\[
\mathrm{tf}_{\mathrm{BM25}}(t, d) = \frac{f \cdot (k_1+1)}{f + k_1 \cdot (1-b + b \cdot |d|/\mathrm{avgdl})}
\]

Log tf damps “this name appears 400 times.” BM25 tf also pulls long documents toward the collection’s average length. *Moby-Dick* would no longer get a linear reward for repeating `whale`. For a teaching snapshot, linear normalized tf is easier to check by hand.

## What to use when

| Goal | Formula |
| --- | --- |
| Match this repo / the original blog toy | raw \(\ln(N/\mathrm{df})\) |
| Tiny corpora where stopwords still rank | smooth \(+1\), or an explicit stoplist |
| Query scoring with unseen terms | add1 form so \(\mathrm{df}=0\) is defined |
| Production ranking | BM25 (full, not just idf) or a learned ranker |
| Compare two implementations | agree on log base, \(N\), and smoothing *before* diffing floats |

## Gutenberg snapshot (qualitative)

On the 18-book collection, switching raw → smooth \(+1\):

- Zeros in Alice (`a`, `about`, `after`) become small positive numbers equal to those words’ tf.
- `alice`, `gryphon`, `ahab` stay at the top. Their idf was already large; adding 1 is a small relative change.
- Mid-list English words (`herself`, `captain`, `have`) climb. That is the “less sparse vector” effect, not a better plot summary.

If you want to see the numbers, run:

```bash
python3 examples/tiny-corpus/compute_tfidf.py --variants
python3 examples/tiny-corpus/compute_tfidf.py --docs examples/tiny-corpus/documents --explain tea --variants
```

The printed table adds `idf_smooth`, `idf_add1`, and `idf_prob` next to the raw column. The written `output/idf.txt` is still raw.
