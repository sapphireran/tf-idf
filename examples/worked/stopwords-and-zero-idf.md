# Stopwords you did not write

221 tokens have `df = 18` and therefore `idf = 0` in the committed snapshot.

```
python3 examples/python/inspect_committed.py --summary
```

```
documents     18
vocabulary    57368
df=1          36887
idf=0         221
dirty_idf     1        # thatyou
```

Those 221 strings still appear in every `output/tfidf/*.txt` file. Their weight is the character `0`. They do not move a cosine. They are the toy's stopword list.

## Function words, as expected

`the`, `and`, `of`, `to`, `a`, `in`, `i`, `you`, `it`, `was`, `said`. Any 18-book English sample will zero these.

The blog post's observation still holds: you do not need a stopword file to drop `the`. You need a corpus in which `the` is actually everywhere.

## Content words that also vanished

Zero IDF is not a linguistic claim about emptiness. It is a claim about **this sample**. The following are ordinary content words that happen to occur in all 18 files:

```
age angry bed breath children dead death eye eyes face faces friend
ground happy house life morning night secret tongue truth water world
```

`death` is in Blake and the Bible and *Macbeth* and *Moby-Dick*. Of course it is. In a corpus of sermons it would be a discriminator. Here it is wallpaper.

`house` and `world` are the same story. *Emma* is about houses; *Paradise Lost* is about a world. Both books use the string, and so does everyone else.

If you add a 19th book that never says `tongue`, `idf(tongue)` becomes `ln(19/18)` and the token starts to matter again. The list is not portable.

## Mid-idf words that look like stopwords but are not

These survive with small positive weight:

| Token | df | idf | Note |
| --- | ---: | ---: | --- |
| `mr` | 10 | 0.588 | Austen / Edgeworth marker |
| `mrs` | 8 | 0.811 | same |
| `thou` | 13 | 0.325 | Early Modern / poetic cluster |
| `thee` | 11 | 0.492 | same |
| `o` | 12 | 0.405 | Whitman's vocative; his top weight |
| `have` | 15 | 0.182 | Chesterton *Ball* still ranks it (modern spelling vs Folio `haue`) |
| `caesar` | 8 | 0.811 | the play, plus history mentions |

`have` at `df = 15` is a reminder that Shakespeare does not always write `have`. The three Folio plays use `haue`. Modern-spelling books use `have`. The tokenizer treats them as unrelated, so `have` is not corpus-wide and `haue` becomes a Shakespeare detector.

## The other tail: 36,887 hapaxes

`df = 1` is 64% of the vocabulary. Most of these never rank. A unique token with `tf ≈ 1/N_tokens` in the Bible is invisible. A unique token that is also a speech prefix (`macb`) or a title character (`buster`, `syme`, `elinor`) dominates its book.

The interesting band is the middle: `df` from 2 to 6, high in-book `tf`. That is `alice` (3), `whale` (6), `gryphon` (2), `hatter` (3), `ahab` (2).

## One dirty cell

`output/idf.txt` contains

```
thatyou	2.89037175789616y
```

`thatyou` is a missing-space join. The trailing `y` is a write glitch. The leading float is `ln(18)`. `inspect_committed.py` reports it as `dirty_idf`. Leave it; the snapshot is historical.

## Practical switches

- `--drop-digits` on `rank_terms.py` hides verse numbers and `1865`.
- A real stop list would still be useful if you wanted themes instead of names. It would have to include `macb`, `ham`, `bru`, and `syme`, which no standard English stop list contains.
- Do not copy the 221 zero-IDF tokens into another project and call them stopwords. They are a photograph of this sample.
