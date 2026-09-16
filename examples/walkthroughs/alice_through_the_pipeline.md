# Walkthrough: one book, four tokens

This page follows *Alice's Adventures in Wonderland* through the
committed `output/` tables. Every figure is a file you can open; the
companion command is:

```bash
python3 examples/follow_word.py alice
python3 examples/follow_word.py the
python3 examples/follow_word.py rabbit
python3 examples/follow_word.py gryphon
```

Collection size for these tables: \(N = 18\).

## The book in the collection

`gutenberg/carroll-alice.txt` is the shortest "famous novel" in the
folder: about 26k `wc` words and 2,753 distinct tokens after the Perl
tokenizer. It is long enough that function words behave like function
words, and short enough that a character name can still take a large
share of TF.

The file begins with the NLTK header line and Chapter I. Those tokens
(`alices`, `adventures`, `wonderland`, `lewis`, `carroll`, `1865`) are
scored. They do not dominate the ranking because they appear once or
twice.

## Token: `alice`

| Stage | Value | Where |
| --- | --- | --- |
| Raw presence | In 3 of 18 books | `output/df.txt` |
| Other owners | `chesterton-thursday.txt`, `edgeworth-parents.txt` | same row |
| IDF | \(\ln(18/3) = 1.79175946922805\) | `output/idf.txt` |
| TF in Carroll | `0.0144867549668874` | `output/tf/carroll-alice.txt` |
| TF-IDF in Carroll | `0.025956780390307` | `output/tfidf/carroll-alice.txt` |

Product check: \(0.0144867549668874 \times 1.79175946922805 \approx
0.02595678\).

`alice` is the top term in this book by a wide margin (next is
`gryphon` at `0.00455`). That is the method working: the name is
common in this file and uncommon in the other 17.

It is *not* unique to Carroll. Chesterton and Edgeworth both use the
ordinary English name. IDF therefore uses 3, not 1. If Alice were a
nonce coinage, IDF would be \(\ln 18 \approx 2.890\) and the product
would be about 1.6× larger. Collection context is part of the score.

## Token: `the`

| Stage | Value |
| --- | --- |
| DF | 18 / 18 |
| IDF | \(\ln(18/18) = 0\) |
| TF in Carroll | `0.0612959060806743` (about 6.1% of all tokens) |
| TF-IDF in Carroll | `0` |

`the` is the most frequent token in the book and contributes nothing
to the ranking. The same zero is written for every other file. This is
why the toy never needed an English stopword list for the Gutenberg
mix: collection-wide words are already annihilated.

If you reran IDF with the script's `$#files` quirk (\(N = 20\)), `the`
would get \(\ln(20/18) \approx 0.10536\) and a Carroll product around
`0.00646` — high enough to sit near `gryphon`. That is the practical
reason the 2012 bugfix mattered.

## Token: `rabbit`

| Stage | Value |
| --- | --- |
| DF | 6 / 18 |
| IDF | \(\ln(18/6) = 1.09861228866811\) |
| TF in Carroll | `0.00161800120409392` |
| TF-IDF in Carroll | `0.00177755600589738` |

`rabbit` is famous in Alice and still only rank 8. Children's stories
(Bryant, Burgess) and Chesterton also mention rabbits, so the IDF is
the same as `whale`'s (\(\mathrm{df} = 6\) as well). High cultural
salience is not the same as high collection rarity.

The product check again holds: \(0.00161800120409392 \times
1.09861228866811 \approx 0.00177756\).

## Token: `gryphon`

| Stage | Value |
| --- | --- |
| DF | 1 / 18 (Carroll only) |
| IDF | \(\ln 18 \approx 2.89037175789616\) |
| TF in Carroll | `0.00206953642384106` |
| TF-IDF in Carroll | `0.00454723629415609` |

`gryphon` is rarer than `alice` and less frequent inside the book.
Maximum IDF compensates enough to put it second. `duchess` and
`dormouse` tie just behind it. That cluster — unique set-piece
creatures — is the "aboutness" list most people expect after the
protagonist's name.

## What to notice

1. **IDF is global.** You cannot interpret a Carroll TF-IDF row without
   knowing how many other files used the word.
2. **TF is local and length-normalized.** `alice` at 1.45% of the
   book's tokens is already a huge concentration.
3. **Zeros are information.** `the` at TF 6% / TF-IDF 0 is a successful
   suppression, not a missing value.
4. **The alphabetical dump hides all of this.** Rank it
   (`examples/rank_terms.py --only carroll-alice.txt`) or trace one
   word (`examples/follow_word.py`) instead of scrolling
   `output/tfidf/carroll-alice.txt` looking for a peak.

The same four-token exercise on *Moby-Dick* (`whale`, `the`, `ahab`,
`moby`) is the natural sequel. `moby` has \(\mathrm{df} = 1\) and
still ranks below `whale` because the common noun is used so much more
often that TF wins.
