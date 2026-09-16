# Selected DF / IDF values from the Gutenberg tables

Source: checked-in `output/df.txt` and `output/idf.txt` with `N = 18`.
`idf = ln(18 / df)`. Filenames in the last column are a sample, not a complete
reprint of the hash dump.

Use this as a lookup while reading the examples, not as a universal IDF table.

## Function words (IDF = 0)

These appear in all 18 files.

| Term | df | idf |
| --- | ---: | ---: |
| `a` | 18 | 0 |
| `and` | 18 | 0 |
| `in` | 18 | 0 |
| `not` | 18 | 0 |
| `of` | 18 | 0 |
| `that` | 18 | 0 |
| `the` | 18 | 0 |
| `to` | 18 | 0 |
| `with` | 18 | 0 |
| `you` | 18 | 0 |

Any TF-IDF row for these terms is `0`. They still have large TF.

## Honorifics and pronouns that survive

They miss at least one file, so IDF is small but not zero.

| Term | df | idf ≈ | Missing-from intuition |
| --- | ---: | ---: | --- |
| `mr` | 10 | 0.58779 | Several plays / poems / KJV never say “Mr.” |
| `mrs` | 8 | 0.81093 | Same, plus some of the men's-adventure texts |
| `thou` | 13 | 0.32542 | Common in verse and KJV; absent from a few modern-ish prose files |
| `thee` | 11 | 0.49248 | Similar to `thou` |
| `o` | 12 | 0.40547 | Vocative; Whitman's TF is huge enough to still rank |

This is why `mr` and `mrs` still appear in the Austen top-12 lists. They are
not “rare words”; they are only rare **in this mixed sample**.

## Character and setting terms

| Term | df | idf ≈ | Files (abbrev.) |
| --- | ---: | ---: | --- |
| `harriet` | 1 | 2.89037 | *Emma* only |
| `knightley` | 1 | 2.89037 | *Emma* only |
| `weston` | 1 | 2.89037 | *Emma* only |
| `fairfax` | 1 | 2.89037 | *Emma* only |
| `elinor` | 1 | 2.89037 | *Sense* only |
| `dashwood` | 1 | 2.89037 | *Sense* only |
| `elliot` | 1 | 2.89037 | *Persuasion* only |
| `wentworth` | 1 | 2.89037 | *Persuasion* only |
| `emma` | 2 | 2.19722 | *Emma*, *Persuasion* (passing mention) |
| `woodhouse` | 2 | 2.19722 | *Emma*, *Moby-Dick* |
| `marianne` | 2 | 2.19722 | *Sense*, Edgeworth |
| `jane` | 3 | 1.79176 | all three Austen novels |
| `anne` | 6 | 1.09861 | *Persuasion* plus Chesterton, *Sense*, Edgeworth, … |
| `queequeg` | 1 | 2.89037 | *Moby-Dick* only |
| `pequod` | 1 | 2.89037 | *Moby-Dick* only |
| `sperm` | 1 | 2.89037 | *Moby-Dick* only (whale) |
| `ahab` | 2 | 2.19722 | *Moby-Dick*, KJV |
| `ishmael` | 2 | 2.19722 | *Moby-Dick*, KJV |
| `whale` | 6 | 1.09861 | Melville, KJV, Whitman, Bryant, two Shakespeare |
| `alice` | 3 | 1.79176 | Carroll, Chesterton *Thursday*, Edgeworth |
| `dormouse` | 1 | 2.89037 | Carroll only |
| `gryphon` | 2 | 2.19722 | Carroll, Milton |
| `macbeth` | 1 | 2.89037 | *Macbeth* only |
| `banquo` | 1 | 2.89037 | *Macbeth* only |
| `macb` | 1 | 2.89037 | *Macbeth* speech prefix |
| `bru` | 1 | 2.89037 | *Caesar* speech prefix |
| `ham` | 5 | 1.28093 | *Hamlet* prefix **and** the common noun/name in other books |
| `brutus` | 2 | 2.19722 | *Caesar*, *Hamlet* |
| `caesar` | 8 | 0.81093 | widely quoted |
| `hamlet` | 6 | 1.09861 | the play plus mentions elsewhere |
| `syme` | 1 | 2.89037 | *Thursday* only |
| `flambeau` | 1 | 2.89037 | Father Brown only |
| `buster` | 1 | 2.89037 | Burgess only |
| `thel` | 1 | 2.89037 | Blake only |
| `lyca` | 1 | 2.89037 | Blake only |

`woodhouse` showing up in *Moby-Dick* is the interesting IDF footgun: a
different Woodhouse (or a passing name) in another public-domain book is
enough to cut Emma's family name from 2.89 down to 2.20.

`ahab` and `ishmael` are the same story against the King James Bible.

## Shared religious / epic vocabulary

| Term | df | idf ≈ | Why it is not a singleton |
| --- | ---: | ---: | --- |
| `unto` | 6 | 1.09861 | KJV plus Melville, Whitman, Bryant, Milton, Shakespeare |
| `saith` | 2 | 2.19722 | KJV and Melville |
| `israel` | 5 | 1.28093 | KJV plus several literary mentions |
| `satan` | 7 | 0.94446 | Milton, KJV, and later prose |
| `adam` | 7 | 0.94446 | same |
| `eve` | 7 | 0.94446 | same (also the common noun *eve*) |

*Paradise Lost* still ranks `satan`, `adam`, and `eve`, but their IDF is
modest. `thee` / `thou` / `heaven` compete because the poem repeats them
constantly.

## Header leakage

| Term | df | idf ≈ | Source |
| --- | ---: | ---: | --- |
| `ebook` | 1 | 2.89037 | `chesterton-ball.txt` Gutenberg boilerplate |
| `gutenberg` | 1 | 2.89037 | same file |

If every transcription had kept the same header, both terms would have
`df = 18` and disappear. Inconsistent front matter is an IDF amplifier.

## How to extend this list

```bash
# DF + files for one term
awk -F'\t' '$1=="whale" {print}' output/df.txt

# IDF
awk -F'\t' '$1=="whale" {print}' output/idf.txt
```

Or add a word to the table in a personal notes file and re-run those lookups.
The Python ranker does not replace this: ranking is per document, while this
page is per term across the corpus.
