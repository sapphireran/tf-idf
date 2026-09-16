# Interpreting the Gutenberg TF-IDF rankings

The files in `output/tfidf/` are alphabetized. This page talks about
the **ranked** view: sort each file by the numeric column, descending.
`examples/python/top_terms.py` does that.

```bash
python3 examples/python/top_terms.py output/tfidf --top 10
```

Numbers below are from the checked-in snapshot (`N = 18`). They will
drift if you change the collection.

## What a high score usually means

A top term is some mix of:

1. The document uses the token a lot (high TF).
2. Few other documents use it (high IDF).

In this collection that mix is almost always a **proper name**, a
**speech prefix**, or a **header leak**. It is rarely an abstract
theme (`love`, `death`, `sea`). Those words are too well shared.

## Book-by-book reading

### Austen: casts, not diction

| File | Top terms (snapshot) |
| --- | --- |
| `austen-emma.txt` | emma, harriet, weston, knightley, elton, mr, fairfax, woodhouse |
| `austen-persuasion.txt` | elliot, wentworth, anne, musgrove, russell, mrs, charles, uppercross |
| `austen-sense.txt` | elinor, marianne, dashwood, jennings, mrs, willoughby, lucy, brandon |

`mr` and `mrs` survive because they are slightly less universal than
`the`, and because dialogue leans on them. They are the first reminder
that "not a stopword" is not the same as "a good keyword."

The useful experiment: the three books share an author and a century
and still split cleanly. TF-IDF is indexing **who is on stage**.

### Carroll: the cleanest protagonist row

`alice`, `gryphon`, `dormouse`, `duchess`, `hatter`, `turtle`,
`caterpillar`, `rabbit`.

This is the row people expect TF-IDF to produce. The protagonist is
frequent and the supporting creatures are rare in the other 17 files.
`alices` appears separately because the tokenizer ate the apostrophe.

### Melville: content words that behave like names

`whale`, `ahab`, `sperm`, `stubb`, `queequeg`, `whales`, `starbuck`,
`pequod`, `nantucket`.

`whale` outranks `ahab` in the snapshot. `whale` has a higher TF and
a weaker IDF (`df = 6` vs `df = 2`). The product still puts both at
the top of *Moby-Dick* and nowhere else in the same way.

`sperm` is a whaling-word ranking, not a failure of the math.

### Bible and Milton: archaic second person

KJV top terms include `unto`, `israel`, `saith`, `thee`, `david`,
`judah`, `thou`. Milton overlaps on `thee`, `thou`, `thy` and then
adds `eve`, `adam`, `satan`.

Two lessons:

- In a mixed modern/early-modern collection, **pronoun morphology**
  is as distinctive as a place name.
- Shared archaic pronouns keep Milton's `thou` from being as extreme
  as `ahab`. The Bible is sitting in the same `N = 18`.

### Shakespeare: the tokenizer wins

| File | Top terms |
| --- | --- |
| `shakespeare-caesar.txt` | bru, brutus, cassi, haue, cassius, antony, caesar |
| `shakespeare-hamlet.txt` | ham, haue, hor, qu, laer, ophe, pol |
| `shakespeare-macbeth.txt` | macb, haue, macbeth, macd, rosse, vpon, vs |

`haue` / `vpon` / `vs` are spelling, not themes. `ham` is the speaker
tag for Hamlet, repeated every speech, almost unique to that file.
The play is scoring its own markup.

If you only remember one caveat from this repository, remember this
row.

### Burgess: one name, huge TF

`buster` at ~0.040 is the largest single score in the snapshot. The
book is short-ish and says the character name constantly, and the
other files do not. TF-IDF will happily report that.

### Chesterton: a boilerplate leak

`chesterton-ball.txt` ranks `turnbull` and `macian` first — and then
`ebook` and `gutenberg`. Unique header language is a perfectly good
rare term. The method cannot tell "character" from "license clause."

`chesterton-thursday.txt` is cleaner: `syme` dominates, then the
other conspiracy names.

### Whitman: vocatives and spelling

`o`, `thee`, `poems`, `pioneers`, `passd`, `chant`, `manhattan`.
Whitman's address (`O`) and clipped past tense (`pass'd` → `passd`)
become "content."

### Bryant and Edgeworth: story-local names

These collections are anthologies. Top terms jump from tale to tale
(`margery`, `jackal`, `epaminondas`, `cecilia`, `piedro`). That is
expected when one file is many plots.

### Blake: short-document spike

`thel`, `weep`, `lyca`. The file is small, so each repeated name is a
large TF. Compare the micro-collection bread document in
[worked-example.md](worked-example.md).

## How to read a single TSV row

Take `alice` in Carroll:

1. `output/tf/carroll-alice.txt` — TF share of the book.
2. `output/idf.txt` — `1.791…` ⇒ `df = 3`.
3. `output/df.txt` — which three files.
4. Product ≈ 0.026, first in that book's ranking.

If a term surprises you, walk those four files before changing the
formula. Most surprises are `df > 1`, markup, or headers.

## What not to do with these scores

- Do not treat the ranking as a plot summary.
- Do not compare raw TF-IDF values **across** documents as "which
  book is more about X." TF is length-normalized inside a document;
  the product is still not a calibrated aboutness score.
- Do not average the 18 files into a "Gutenberg embedding." That is a
  different project.
- Do not drop the snapshot into a search engine without a stopword
  list, a stemmer, and a decision about markup.

## A quick self-check

If you reimplement the math and your top-10 for `melville-moby_dick.txt`
does not start with some permutation of `whale` / `ahab` / `sperm` /
`stubb` / `queequeg`, the collection changed or the tokenizer diverged.
Start with [output-formats.md](output-formats.md) and the tests under
`tests/`.
