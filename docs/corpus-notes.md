# Corpus notes (NLTK Gutenberg sample)

`gutenberg/` is the 18-file sample that ships with NLTK's `gutenberg`
corpus, not a custom crawl. The filenames are NLTK's (`carroll-alice.txt`,
`melville-moby_dick.txt`, …). The texts are public-domain works from Project
Gutenberg, with NLTK's usual light packaging (a one-line title header on
several files).

I did not re-download these for the personal toy pipeline. Whatever NLTK
had when the files were first copied in is what the Perl scored.

## The 18 files

| Filename | Author | Work | Genre / form | `wc -w` |
| --- | --- | --- | --- | ---: |
| `austen-emma.txt` | Jane Austen | *Emma* | Novel | 158,167 |
| `austen-persuasion.txt` | Jane Austen | *Persuasion* | Novel | 83,308 |
| `austen-sense.txt` | Jane Austen | *Sense and Sensibility* | Novel | 118,675 |
| `bible-kjv.txt` | (KJV) | King James Bible | Scripture | 821,133 |
| `blake-poems.txt` | William Blake | Poems (Songs of Innocence / Experience and others) | Poetry | 6,845 |
| `bryant-stories.txt` | Stories collected as Bryant | Short stories | 45,988 |
| `burgess-busterbrown.txt` | Thornton W. Burgess | *The Adventures of Buster Bear* (NLTK label: Buster Brown) | Children's | 15,870 |
| `carroll-alice.txt` | Lewis Carroll | *Alice's Adventures in Wonderland* | Children's / nonsense | 26,443 |
| `chesterton-ball.txt` | G. K. Chesterton | *The Ball and the Cross* | Novel | 81,598 |
| `chesterton-brown.txt` | G. K. Chesterton | Father Brown stories | Detective | 71,626 |
| `chesterton-thursday.txt` | G. K. Chesterton | *The Man Who Was Thursday* | Novel | 57,955 |
| `edgeworth-parents.txt` | Maria Edgeworth | *The Parent's Assistant* | Children's tales | 166,070 |
| `melville-moby_dick.txt` | Herman Melville | *Moby-Dick* | Novel | 212,030 |
| `milton-paradise.txt` | John Milton | *Paradise Lost* | Epic poem | 79,659 |
| `shakespeare-caesar.txt` | Shakespeare | *Julius Caesar* | Play | 20,459 |
| `shakespeare-hamlet.txt` | Shakespeare | *Hamlet* | Play | 29,605 |
| `shakespeare-macbeth.txt` | Shakespeare | *Macbeth* | Play | 17,741 |
| `whitman-leaves.txt` | Walt Whitman | *Leaves of Grass* | Poetry | 122,070 |

`wc -w` is whitespace word count on the raw files. The Perl tokenizer's
`tokens(d)` is a different number because it splits on spaces *after*
punctuation is deleted, and it increments the counter even for empty fields.
See [perl-pipeline.md](perl-pipeline.md).

## Why this collection is a good TF-IDF demo

The mix is intentionally unfair, which is the point:

- **Three Austens** share a social vocabulary (`mr`, `mrs`, `miss`,
  `gentleman`). IDF down-weights those across the Austen trio but they still
  beat biblical diction inside *Emma*.
- **Three Chestertons** share an authorial voice. Comparing Thursday vs
  Father Brown with `examples/compare_documents.py` is a sanity check:
  same-author pairs should outrank Alice vs the Bible.
- **Three Shakespeare plays** keep speech prefixes and Early Modern
  spelling, so TF-IDF surfaces `haue` / `vpon` / `macb` instead of "ambition"
  or "ghost". That is a tokenizer lesson, not a literature lesson.
- **The KJV** is four times longer than *Moby-Dick*. Length-normalized TF is
  the only reason Blake's `thel` can compete with biblical names.
- **Children's books** (Carroll, Burgess, Edgeworth) leak first names into
  each other's DF. `alice` is not unique to Carroll.

## Tokenizer traps in these particular files

### Title headers

Several files start with a bracketed title line, for example:

```
[Alice's Adventures in Wonderland by Lewis Carroll 1865]
```

After lowercasing and stripping punctuation this becomes tokens like
`alices`, `adventures`, `in`, `wonderland`, `by`, `lewis`, `carroll`,
`1865`. That is why `1865` has a TF-IDF row in `carroll-alice.txt`, and why
`alices` (possessive, header, and in-text "Alice's") is a separate term from
`alice`.

### Stage names and speech prefixes

The Shakespeare files look like this conceptually:

```
HAM.  To be, or not to be
```

The tokenizer does not know that `HAM` is a speaker label. In the checked-in
Hamlet table the top TF-IDF term is `ham`, not `hamlet`. Macbeth's top term
is `macb`. If you want "real words" you have to filter those labels by hand.

### Early Modern spelling

`have` → `haue`, `upon` → `vpon`, `give` → `giue`, `loved` → `loue`. TF-IDF
happily treats these as rare, distinctive terms because Austen never spells
them that way. They *are* distinctive — of the encoding, not of the plot.

### Bible verse machinery

`bible-kjv.txt` contains chapter and verse numbers. Those become tokens
(`1001`, `1010`, …) with `df = 1` and the maximum IDF. They pollute
"top terms for the Bible" unless you drop `[0-9]+`.

### Hyphens, apostrophes, and smashed words

The Perl class `[^a-zA-Z\d\s]` is deleted, not replaced with a space:

- `waistcoat-pocket` → `waistcoatpocket`
- `Alice's` → `alices`
- `don't` → `dont`
- `the end.` glued to the next sentence can survive as `themand` if a
  newline/space goes missing in the source

Those wrecked tokens show up in `examples/top_terms.py` output. They are
honest artifacts, not OCR from a different edition.

### `.DS_Store` is not a document

macOS left a `.DS_Store` in `gutenberg/` in some checkouts. The Perl
`readdir` loop skips names that start with `.` when *writing TF files*, but
it still counts those directory entries when it sets `N = $#files`. The
checked-in IDF table used `N = 18` anyway. Do not add hidden files if you
want a rerun to match `output/idf.txt`.

## What I am not doing with these texts

- No stemming, no lemmatization, no stopword file. IDF is the stopword list.
- No sentence splitting. Newlines are just more whitespace.
- No distinction between dialogue and narration.
- No attempt to union the three Austens or the three Shakespeares into
  "author documents." Each file is one document. That choice makes
  `mr` / `mrs` less unique than they would be in a 16-document collection
  that kept a single Austen blob.

If I ever want author-level IDF, the move is to concatenate per author
*before* `tf-idf-values.pl`, not to average the existing TF-IDF tables.
Averaging scores from different document lengths is not the same model.
