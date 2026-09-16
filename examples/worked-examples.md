# Worked examples from the Gutenberg snapshot

Every number in this file was read from the checked-in `output/` tables, not
re-derived from a fresh Perl run. The tokenizer and the `N = 18` IDF are
described in `docs/perl-pipeline.md`.

The identity I am checking each time:

```
tfidf(t, d)  ==  tf(t, d) * idf(t)
idf(t)       ==  ln( 18 / df(t) )
```

## 1. `alice` in *Alice's Adventures in Wonderland*

**Files**

```
output/tf/carroll-alice.txt      alice	0.0144867549668874
output/idf.txt                   alice	1.79175946922805
output/tfidf/carroll-alice.txt   alice	0.025956780390307
output/df.txt                    alice	3	chesterton-thursday.txt, carroll-alice.txt, edgeworth-parents.txt
```

**IDF**

```
df(alice) = 3
idf       = ln(18 / 3) = ln(6) = 1.791759469228055
```

Matches `output/idf.txt` to the digits it stored.

**Product**

```
0.0144867549668874 * 1.79175946922805 = 0.02595678039030698
```

Matches `output/tfidf/carroll-alice.txt`.

**Why it wins the file.** A 1.45% TF is enormous for a content word — that
is roughly one token in seventy. The name also appears in two other NLTK
files, so it does not get the maximum IDF of `ln(18) ≈ 2.890`. It does not
need to. Second place (`gryphon`, below) has a much smaller TF.

**Possessive split.** `Alice's` is stored as `alices` (apostrophe deleted,
`s` kept). That is a different row (`tfidf ≈ 0.001305`) and does not add
into the `alice` count.

## 2. `gryphon` in the same book

`gryphon` is the second-highest TF-IDF term in Carroll.

```
output/tf/carroll-alice.txt      gryphon	0.00206953642384106
output/idf.txt                   gryphon	2.19722457733622
output/tfidf/carroll-alice.txt   gryphon	0.00454723629415609
output/df.txt                    gryphon	2	milton-paradise.txt, carroll-alice.txt
```

Not unique: *Paradise Lost* also uses the word. `df = 2` gives the same IDF
as `ahab` and `emma`:

```
idf = ln(18 / 2) = ln(9) = 2.197224577336220
0.00206953642384106 * 2.19722457733622 = 0.00454723629415609
```

The Gryphon is about 7 times rarer *inside Alice* than the name Alice
(`0.01449 / 0.00207 ≈ 7.0`) but only about 5.7 times smaller as a TF-IDF
score (`0.02596 / 0.00455 ≈ 5.7`), because its IDF is larger
(`2.197 / 1.792 ≈ 1.23`). That is the weighting doing a modest amount of
work. A term that really is unique (`df = 1`, IDF `2.890`) would get a
bigger lift — several of the lower Alice-only nouns (`dormouse`,
`duchess`, `dodo`) live in that bucket.

## 3. `the` in Alice (and everywhere)

```
output/tf/carroll-alice.txt     the	0.0612959060806743
output/idf.txt                  the	0
output/tfidf/carroll-alice.txt  the	0
output/df.txt                   the	18	…every book…
```

```
idf(the) = ln(18 / 18) = ln(1) = 0
tfidf    = tf * 0 = 0
```

Pass 2 still writes the row. A zero in `output/tfidf/` is therefore
ambiguous on its own: either the term is a collection-wide word, or it
somehow missed `idf.txt`. Check `output/idf.txt` to tell the difference.

The same zero-IDF club includes `a` and `and`. They are the closest thing
this pipeline has to a stopword list.

## 4. `whale` and `ahab` in *Moby-Dick*

```
output/tf/melville-moby_dick.txt      whale	0.0044997028498118
output/tfidf/melville-moby_dick.txt   whale	0.00494342884615816
output/idf.txt                        whale	1.09861228866811

output/tf/melville-moby_dick.txt      ahab	0.00196685124567246
output/tfidf/melville-moby_dick.txt   ahab	0.00432161389695589
output/idf.txt                        ahab	2.19722457733622
```

**IDF checks**

```
ln(18 / 6) = ln(3) = 1.098612288668110
ln(18 / 2) = ln(9) = 2.197224577336220
```

Products:

```
whale: 0.0044997028498118 * 1.09861228866811 = 0.004943428846158
ahab:  0.00196685124567246 * 2.19722457733622 = 0.004321613896956
```

`whale` is the more *frequent* Melville word; `ahab` is the more
*collection-rare* word (`df = 2` vs `df = 6`). Their TF-IDF values land
in the same ballpark, which is the weighting doing its job. Melville says
`whale` more than twice as often as `ahab` after this tokenizer
(`0.00450 / 0.00197 ≈ 2.29`). Ahab still almost catches up because a third
as many books mention him.

`sperm`, `stubb`, `queequeg`, `starbuck`, and `pequod` fill out the rest of
the top ten. Those are the terms I would expect a human highlighter to
circle. TF-IDF is working on this file.

## 5. `emma` in *Emma*

```
output/tf/austen-emma.txt      emma	0.00474787578393688
output/tfidf/austen-emma.txt   emma	0.0104321493626056
output/idf.txt                 emma	2.19722457733622
```

```
0.00474787578393688 * 2.19722457733622 = 0.010432149362606
```

`idf = ln(18/2)` so some other book also contains the string `emma`
(almost certainly as a first name, not as Austen's title). The score is
still the clear winner inside `austen-emma.txt`, ahead of `harriet`,
`weston`, `knightley`, and `elton` — the other proper names the plot
actually turns on.

Austen function words (`mr`, `mrs`) appear in the top twenty with *lower*
IDF because the other two Austen novels keep those titles in circulation.
They are distinctive versus Milton, not versus *Persuasion*.

## 6. Shakespeare: when the top term is a speech prefix

```
output/tfidf/shakespeare-hamlet.txt    ham	0.014075
output/tfidf/shakespeare-macbeth.txt   macb	0.021556
```

`HAM.` / `MACB.` speaker labels survive tokenization as `ham` / `macb`.
They are short, repeated on almost every speech, and unique to that play
(so they get a high IDF). The pipeline is not wrong — it was never told
what a speaker label is.

`hamlet` itself is present (`tfidf ≈ 0.003582`) and has a softer IDF
(`1.09861 = ln(18/6)`), because other books mention Hamlet.

If I want "words a reader would name," I drop tokens that look like the
abbreviated speaker column. I do not change `output/` for that. Filtering
is a reading step; the snapshot stays faithful to the Perl.

## 7. Blake: a short document can still win

```
output/tfidf/blake-poems.txt   thel	0.005581
```

Blake is the smallest file (`wc -w` ≈ 6,845). Length-normalized TF gives
*Thel* a real chance against names that appear more often in absolute
counts in the Bible. If pass 1 had used raw counts, this row would be
invisible next to KJV proper nouns.

## 8. Reconstructing `tokens(d)` from a known count

For Alice, a case-insensitive whole-word grep of `alice` on the raw file
reports 398 hits. Those hits are the word `Alice` / `ALICE` / `alice`, not
`Alice's` (the possessive became `alices`).

```
tokens(d) ≈ 398 / 0.0144867549668874 ≈ 27,473
wc -w carroll-alice.txt               = 26,443
```

The extra ~1,030 in the Perl denominator is the empty-token increment
described in `docs/perl-pipeline.md`, plus any `alice` count mismatch if
the tokenizer splits a heading differently than `grep -oiw`. The TF-IDF
product still internally consistent; the denominator is just not `wc -w`.

## 9. What I run after rereading this file

```bash
python3 examples/top_terms.py --doc carroll-alice --n 8
python3 examples/top_terms.py --doc melville-moby_dick --n 8
python3 examples/compare_documents.py --a austen-emma --b austen-sense
python3 examples/compare_documents.py --a austen-emma --b bible-kjv
```

The two Austen novels should be much closer than Emma vs the KJV. If they
are not, the snapshot and this write-up have drifted.
