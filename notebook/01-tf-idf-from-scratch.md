# 01 — TF-IDF from scratch

A term is informative in a document when it is **common in that
document** and **uncommon on the rest of the shelf**. TF-IDF is the
family of products that encode those two observations.

This note is the derivation I wish the 2012 scripts had sat next to.

## Term frequency

Let \(f_{t,d}\) be the raw count of term \(t\) in document \(d\), and
let \(|d|\) be the number of tokens in \(d\).

| Name | Formula | What it emphasizes |
| --- | --- | --- |
| Raw (`n`) | \(f_{t,d}\) | Long documents dominate |
| Length-normalized (`l`, used in the Perl) | \(f_{t,d} / \|d\|\) | Share of the document |
| Log (`l` in some SMART tables) | \(1 + \log f_{t,d}\) if \(f>0\), else 0 | Dampens "the word appears 400 times" |
| Boolean (`b`) | 1 if \(f>0\), else 0 | Presence only |
| Augmented | \(0.5 + 0.5 \cdot f_{t,d} / \max_{t'} f_{t',d}\) | Relative to the document's peak term |

The Perl toy uses length-normalized TF. That is a reasonable default
for a mixed-length shelf: the King James Bible should not win every
query merely by being long.

A quiet bug in the specimen: the Perl increments `|d|` for empty
strings created by its splitter, then throws those empties out of the
TF map. The numerator and the denominator are therefore not quite the
same token sequence. See [03](03-original-perl-walkthrough.md).

## Document frequency and IDF

Let \(N\) be the number of documents and \(n_t\) the number of
documents that contain \(t\) at least once.

\[
\mathrm{idf}(t) = \log \frac{N}{n_t}
\]

is the textbook form and the one the Perl writes to `output/idf.txt`
(natural log, \(N = 18\) after the 2012 "number of files" correction).

Properties I keep on a scrap of paper:

- If \(t\) appears in every document, \(\mathrm{idf}(t) = 0\). The
  product is then zero no matter how large TF is. That is why `the`,
  `and`, and `of` vanish from the historical TF-IDF tables even though
  their TF files are full of them.
- If \(t\) appears in one document, \(\mathrm{idf}(t) = \log N\). On
  this shelf that is \(\log 18 \approx 2.89037\), which is exactly the
  value stamped on hapax-document terms in `output/idf.txt`.
- IDF is a property of the **shelf**, not of a document. Replacing
  *Moby-Dick* with a cookbook would change `whale`'s IDF everywhere.

Natural log versus \(\log_{10}\) only rescales every weight by a
constant. Rankings that use a single IDF flavor are invariant to that
choice. Rankings that mix flavors are not.

## The product

\[
\mathrm{tfidf}(t, d) = \mathrm{tf}(t, d) \cdot \mathrm{idf}(t)
\]

The 2012 second script (`tf*idf-product.pl`) does exactly this:
read `output/tf/$file` and `output/idf.txt`, multiply, write
`output/tfidf/$file`.

That product is a **term weight inside a document**. It is not yet a
query score. To rank documents you still need a rule for combining the
query's terms — sum of weights, cosine, BM25, and so on. That is
[06](06-ranking-and-cosine.md).

## SMART notation, briefly

Classical IR papers name a weighting pair with three letters for the
document and three for the query, for example `ltc.ltn`:

1. TF flavor (`n` raw, `l` log, `a` augmented, `b` boolean)
2. IDF flavor (`n` none, `t` `log(N/n_t)`, `p` probabilistic)
3. Normalization (`n` none, `c` cosine)

The Perl specimen is closest to **`ntn` on the document side** if you
treat length-normalized TF as the TF component and skip vector
normalization: normalized TF, inverse-document IDF, no cosine. I do
not pretend the specimen was written against the SMART tables. The
notation is just a way to notice that "TF-IDF" is a *menu*.

## What the product is not

- It is not a probability. The numbers are not calibrated and need not
  sum to one.
- It is not semantics. `bank` in a river memoir and `bank` in a
  counting-house novel share a token.
- It is not robust to OCR, play-text stage directions, or chapter
  headings. Those strings become "terms" with high IDF because they
  are typographically rare, not because they are thematically rare.

The tiny-corpus arithmetic in [04](04-worked-example-tiny-corpus.md) is
the check that I actually understand the menu I just wrote down.
