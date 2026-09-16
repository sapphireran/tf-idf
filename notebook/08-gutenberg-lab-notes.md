# 08 — Gutenberg shelf observations

Numbers below were produced by `python3 -m tfidf` in this pass
(`simple` tokenizer, classic IDF unless named otherwise). They are
not copied from the 2012 `output/` fossil. If a later tokenizer
change moves them, update this page; do not silently "fix" the books.

## Token counts

`python3 -m tfidf corpus-stats --corpus gutenberg`

| document | tokens | types |
| --- | ---: | ---: |
| bible-kjv.txt | 854046 | 12744 |
| melville-moby_dick.txt | 218619 | 17139 |
| edgeworth-parents.txt | 170799 | 8342 |
| austen-emma.txt | 161980 | 7103 |
| whitman-leaves.txt | 126605 | 12405 |
| austen-sense.txt | 120787 | 6336 |
| austen-persuasion.txt | 84167 | 5777 |
| chesterton-ball.txt | 82869 | 8235 |
| milton-paradise.txt | 80497 | 8979 |
| chesterton-brown.txt | 73288 | 7739 |
| chesterton-thursday.txt | 58729 | 6305 |
| bryant-stories.txt | 46699 | 3836 |
| shakespeare-hamlet.txt | 30271 | 4701 |
| carroll-alice.txt | 27336 | 2570 |
| shakespeare-caesar.txt | 20875 | 3019 |
| shakespeare-macbeth.txt | 18351 | 3451 |
| burgess-busterbrown.txt | 16359 | 1527 |
| blake-poems.txt | 6936 | 1512 |

\(N = 18\), average length \(\approx 122178\). The Bible is about
123× Blake. Any ranking rule that forgets length will let scripture
hoard common query terms. Cosine and BM25 both have a length story;
raw TF does not.

*Moby-Dick* has the most **types** (17139), not the most tokens.
That matches the book's reputation for a wide technical vocabulary
(whaling gear, cetology asides) more than it matches raw bulk.

## Distinctive terms

`--alpha-only` drops tokens that contain a digit (title-line years,
act numbers).

### Alice (`carroll-alice.txt`)

| term | tf-idf |
| --- | ---: |
| alice | 0.026087 |
| duchess | 0.004441 |
| gryphon | 0.004421 |
| dormouse | 0.004229 |
| hatter | 0.003671 |
| turtle | 0.002765 |
| rabbit | 0.002050 |
| caterpillar | 0.001835 |

That is a children's novel, not a random slice of Victorian prose.

Historical Perl product for `alice` is `0.025957` (`output/tfidf/`).
Same order of magnitude; the gap is the tokenizer / empty-token
denominator, not a different \(N\). Historical IDF for `alice` is
\(\ln(18/3) = \ln 6 \approx 1.79176\), so the name appears in three
files on the shelf.

### *Moby-Dick* (`melville-moby_dick.txt`)

| term | tf-idf |
| --- | ---: |
| whale | 0.006161 |
| ahab | 0.005136 |
| stubb | 0.003398 |
| queequeg | 0.003332 |
| starbuck | 0.002618 |
| sperm | 0.002452 |
| pequod | 0.002287 |
| whales | 0.001844 |

`explain whale --doc gutenberg/melville-moby_dick.txt`:

- raw count 1226 in 218619 tokens
- document frequency 6 (Bible, Bryant, Chesterton's *Ball*,
  *Moby-Dick*, *Hamlet*, Whitman)
- classic product \(0.005608 \times \ln(18/6) \approx 0.006161\)

So `whale` is *not* a hapax on this shelf. It still wins inside
Melville because the TF is huge. Bryant's children's stories also
mention whales, which is why Bryant keeps showing up as a distant
second on whale queries.

### Macbeth (`shakespeare-macbeth.txt`)

| term | tf-idf |
| --- | ---: |
| macb | 0.021578 |
| haue | 0.011912 |
| macbeth | 0.009765 |
| macd | 0.009135 |
| rosse | 0.007718 |
| banquo | 0.006143 |
| vpon | 0.006054 |
| thane | 0.003938 |

This listing is a tokenizer lesson:

- `macb` / `macd` are speech prefixes (`Macb.`, `Macd.`), not
  vocabulary I would highlight in an essay.
- `haue`, `vpon` are Early Modern spellings. They look "distinctive"
  because the three Austen novels do not share them, not because
  they are thematically Macbeth.
- The 2012 Perl tables also contain smashed crumbs such as
  `1murth`. The `simple` tokenizer splits digits from letters, so
  those exact strings do not appear here. The *kind* of junk is the
  same: play markup leaking into the term space.

`--stopwords` does not remove `haue`. A stoplist trained on modern
English will not save you from 1603.

## Query ranks (cosine / classic)

All six sanity queries from [02](02-corpus-notes.md) put the obvious
book first. Gaps are large except where noted.

| query | #1 | score | #2 | score |
| --- | --- | ---: | --- | ---: |
| `white whale ahab` | melville-moby_dick.txt | 0.592 | bryant-stories.txt | 0.017 |
| `alice rabbit queen` | carroll-alice.txt | 0.818 | bryant-stories.txt | 0.012 |
| `macbeth witches thane` | shakespeare-macbeth.txt | 0.249 | milton-paradise.txt | 0.001 |
| `emma woodhouse hartfield` | austen-emma.txt | 0.473 | austen-persuasion.txt | 0.001 |
| `father brown flambeau` | chesterton-brown.txt | 0.587 | burgess-busterbrown.txt | 0.004 |
| `hamlet ghost horatio` | shakespeare-hamlet.txt | 0.173 | whitman-leaves.txt | 0.001 |
| `paradise satan eden` | milton-paradise.txt | 0.131 | edgeworth-parents.txt | 0.010 |

`father brown` vs `busterbrown` is the kind of token collision I
want to remember: the filename and the children's bear story share
`brown`, but `flambeau` is enough to keep Chesterton first.

## Smoothing comparison on `white whale`

| scheme | #1 | #2 | #3 |
| --- | --- | --- | --- |
| cosine / classic | *Moby-Dick* 0.495 | Bryant 0.038 | Whitman 0.008 |
| cosine / smooth | *Moby-Dick* 0.107 | Bryant 0.010 | Blake 0.009 |
| cosine / probabilistic | *Moby-Dick* 0.158 | Blake 0.090 | Bryant 0.070 |
| BM25 | *Moby-Dick* 2.664 | Bryant 2.574 | Whitman 2.199 |

Every flavor still elects Melville. BM25's margin over Bryant is
thin because both books use `whale` and BM25 saturates TF: the
1226th Melville occurrence is worth much less than the first.
Cosine, using length-normalized TF without saturation, keeps a
wide gap. That is the first time in this lab I have *seen*
saturation instead of only writing the formula down.

Smooth IDF shrinks the scores (a floor on common words dilutes
the vector toward function words). Probabilistic IDF lets Blake
climb, which I do not yet fully trust — short verse plus negative
weights on majority terms is a twitchy combination on \(N=18\).

## Reading the 2012 `output/` snapshot

I am not regenerating those files. They remain a Perl fossil.

Useful fossils:

- `output/idf.txt` hapax lines equal \(\ln 18 \approx 2.89037175789616\).
- `output/tfidf/carroll-alice.txt` has `a` at 0 (collection-wide).
- `output/tfidf/melville-moby_dick.txt` has `whale ≈ 0.00494`,
  `ahab ≈ 0.00432` under the Perl tokenizer. Same story, different
  token rules.

Known disagreements with the Python lab are listed in
[03](03-original-perl-walkthrough.md).
