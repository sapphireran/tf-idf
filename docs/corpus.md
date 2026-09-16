# Gutenberg sample

`gutenberg/` holds **18** plain-text Project Gutenberg transcriptions. They are
the documents `N = 18` refers to in the checked-in IDF table.

A macOS leftover, `gutenberg/.DS_Store`, sits in the same directory. The
checked-in `output/tf/` listing has no `.DS_Store` file, so that binary was
not part of the 2012 run. `tf-idf-values.pl` will try to read it on a fresh
run because the name does not start with `.`.

## Inventory

Word counts are `wc -w` on the raw files (whitespace-separated tokens **before**
this repo's tokenizer). Unique-term counts are the number of lines in
`output/tf/<file>`, i.e. the vocabulary after tokenization.

| File | Work | Bytes | `wc -w` | Unique terms |
| --- | --- | ---: | ---: | ---: |
| `austen-emma.txt` | Jane Austen, *Emma* | 887,071 | 158,167 | 9,312 |
| `austen-persuasion.txt` | Jane Austen, *Persuasion* | 466,292 | 83,308 | 5,990 |
| `austen-sense.txt` | Jane Austen, *Sense and Sensibility* | 673,022 | 118,675 | 7,335 |
| `bible-kjv.txt` | King James Bible | 4,332,554 | 821,133 | 16,567 |
| `blake-poems.txt` | William Blake, *Songs of Innocence and of Experience* and *The Book of Thel* | 38,153 | 6,845 | 1,542 |
| `bryant-stories.txt` | Sara Cone Bryant, children's stories | 249,439 | 45,988 | 4,011 |
| `burgess-busterbrown.txt` | Thornton Burgess, *The Adventures of Buster Bear* (filename says Buster Brown) | 84,663 | 15,870 | 1,568 |
| `carroll-alice.txt` | Lewis Carroll, *Alice's Adventures in Wonderland* | 144,395 | 26,443 | 2,753 |
| `chesterton-ball.txt` | G. K. Chesterton, *The Ball and the Cross* | 457,450 | 81,598 | 8,646 |
| `chesterton-brown.txt` | G. K. Chesterton, Father Brown stories | 406,629 | 71,626 | 8,235 |
| `chesterton-thursday.txt` | G. K. Chesterton, *The Man Who Was Thursday* | 320,525 | 57,955 | 6,524 |
| `edgeworth-parents.txt` | Maria Edgeworth, *The Parent's Assistant* | 935,158 | 166,070 | 9,561 |
| `melville-moby_dick.txt` | Herman Melville, *Moby-Dick* | 1,242,990 | 212,030 | 19,961 |
| `milton-paradise.txt` | John Milton, *Paradise Lost* | 468,220 | 79,659 | 9,321 |
| `shakespeare-caesar.txt` | Shakespeare, *Julius Caesar* | 112,310 | 20,459 | 3,091 |
| `shakespeare-hamlet.txt` | Shakespeare, *Hamlet* | 162,881 | 29,605 | 4,799 |
| `shakespeare-macbeth.txt` | Shakespeare, *Macbeth* | 100,351 | 17,741 | 3,560 |
| `whitman-leaves.txt` | Walt Whitman, *Leaves of Grass* | 711,215 | 122,070 | 14,568 |

**Totals:** about 11.3 MB of text, ~2.14 million `wc -w` tokens, **57,368**
distinct terms in `output/idf.txt`.

## Why this mix is a useful TF-IDF toy

The collection is small enough to run in one pass and diverse enough that IDF
has something to do:

- **Three Austen novels** share register (`mr`, `mrs`, drawing-room verbs) but
  almost no character names. TF-IDF separates them cleanly. See
  [`../examples/compare-austen-novels.md`](../examples/compare-austen-novels.md).
- **Three Shakespeare plays** share Early Modern spelling (`haue`, `vs`,
  `vpon`) and Folio speech prefixes. IDF only partly removes the shared
  spelling; the prefixes stay document-specific. See
  [`../examples/shakespeare-speaker-tags.md`](../examples/shakespeare-speaker-tags.md).
- **Three Chesterton books** share an authorial vocabulary; the distinctive
  leftovers are character names (`syme`, `flambeau`, `turnbull`).
- **One very long religious text** (`bible-kjv.txt`) contributes archaisms
  (`unto`, `saith`, `hath`) that also leak into Milton and Melville, so those
  words get mid-range IDF instead of singleton IDF.
- **Short name-heavy fiction** (Burgess, Carroll, Blake's *Thel*) produces
  larger peak TF-IDF values than *Moby-Dick*, because the denominator
  `tokens(d)` is smaller.

## Filename convention

`author-title.txt`, lowercase, hyphenated. The scripts never parse the names;
they are just document IDs. `output/df.txt` repeats those filenames in the
third column.

## Edition artifacts that leak into the vocabulary

- **Project Gutenberg headers.** `chesterton-ball.txt` still contains boilerplate,
  which is why `ebook` and `gutenberg` appear among that file's stronger TF-IDF
  terms (`df = 1` for both in this sample).
- **Folio / old-spelling Shakespeare.** `haue` (have), `selfe`, `loue`, `vs`
  (us), `vpon` (upon). These are real tokens after the tokenizer strips
  punctuation and lowercases.
- **Speech prefixes.** `macb`, `macd`, `ham`, `bru`, `cassi`, `ophe` — abbreviated
  speaker tags from the play text.
- **Glued tokens.** The tokenizer deletes punctuation without inserting a space.
  `28th-and` can become `28thand`; `Emma's` becomes `emmas` only if the
  apostrophe is stripped between letters — here `'s` becomes `s` attached or
  split depending on the original characters. See
  [`tokenizer-and-quirks.md`](tokenizer-and-quirks.md).
- **Numbers and Gutenberg catalog IDs.** `output/idf.txt` begins with strings
  like `00021053` from *Paradise Lost* notes or headers.

None of this is cleaned in the 2012 scripts. The examples treat those tokens as
part of the demonstration, not as bugs to silently ignore.

## What is not in the sample

No modern web text, no scanned OCR dump beyond Gutenberg's own cleanup, no
non-English works, and no duplicate editions of the same title. IDF values
here are **not** portable to a news crawl or a Wikipedia dump; they describe
this 18-document mix only.
