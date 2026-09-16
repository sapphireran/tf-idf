# TF versus TF-IDF on the same tokens

Same tokenizer, same documents, two rankings. The only change is
whether you multiply by `ln(N / df)`.

## Kitchen vignette

`examples/tiny-corpus/kitchen.txt` is 31 tokens. Top **term frequency**:

| rank | term | tf | idf | tf*idf |
| ---: | --- | ---: | ---: | ---: |
| 1 | the | 0.2581 | 0.0000 | 0.0000 |
| 2 | soup | 0.1613 | 1.6094 | 0.2596 |
| 3 | cook | 0.0968 | 1.6094 | 0.1558 |
| 4 | added | 0.0323 | 1.6094 | 0.0519 |
| 4 | and | 0.0323 | 1.6094 | 0.0519 |
| 4 | from | 0.0323 | 1.6094 | 0.0519 |
| 4 | needs | 0.0323 | 1.6094 | 0.0519 |
| 8 | on | 0.0323 | 0.9163 | 0.0296 |

`the` wins TF because the paragraph is English. After IDF it scores
exactly 0 (`df = 5 = N`). `on` appears in kitchen and in
`stars.txt` (`df = 2`), so it keeps some IDF but drops out of the
tf*idf top 8, replaced by unique once-words such as `salt` and `rose`
(from "steam rose").

Top **tf*idf** is `soup`, then `cook`. That is the intended fingerprint.

## Alice in Wonderland

From the committed Gutenberg tables (`output/tf/carroll-alice.txt` and
`output/tfidf/carroll-alice.txt`).

Top 12 by **normalized TF**:

| rank | term | tf | idf | tf*idf |
| ---: | --- | ---: | ---: | ---: |
| 1 | the | 0.061296 | 0 | 0 |
| 2 | and | 0.031758 | 0 | 0 |
| 3 | to | 0.027130 | 0 | 0 |
| 4 | a | 0.023593 | 0 | 0 |
| 5 | she | 0.020206 | 0 | 0 |
| 6 | it | 0.019792 | 0 | 0 |
| 7 | of | 0.019115 | 0 | 0 |
| 8 | said | 0.017384 | 0 | 0 |
| 9 | i | 0.015051 | 0 | 0 |
| 10 | alice | 0.014487 | 1.7918 | 0.025957 |
| 11 | in | 0.013772 | 0 | 0 |
| 12 | you | 0.013546 | 0 | 0 |

`alice` is only the tenth most common token. The nine words above it
appear in every book in this collection, so IDF wipes them out.

Top 8 by **tf*idf**:

| rank | term | tf*idf | tf | idf | why it ranks |
| ---: | --- | ---: | ---: | ---: | --- |
| 1 | alice | 0.025957 | 0.014487 | ln(18/3) | high TF, df = 3 |
| 2 | gryphon | 0.004547 | 0.002070 | ln(18/2) | rare creature name |
| 3 | dormouse | 0.004242 | 0.001467 | ln(18/1) | unique to this file |
| 3 | duchess | 0.004242 | 0.001467 | ln(18/1) | unique to this file |
| 5 | hatter | 0.003708 | 0.002070 | ln(18/3) | slightly more common in the collection |
| 6 | turtle | 0.003169 | 0.002107 | ln(18/4) | Mock Turtle, but `turtle` is not unique |
| 7 | caterpillar | 0.001820 | 0.001016 | ln(18/3) | |
| 8 | rabbit | 0.001778 | 0.001618 | ln(18/6) | more TF than `dormouse`, more df too |

`rabbit` is a clean illustration of the tradeoff: it is said often in
*Alice*, and it also wanders into other books, so IDF cuts it. The
Dormouse is a worse story-word by TF and a better fingerprint by
tf*idf.

`alices` (from `Alice's`) shows up just under `rabbit` with a tiny TF
and maximum IDF. That is the apostrophe-stripping rule from
[05-quirks-and-limitations.md](05-quirks-and-limitations.md), not a
second character.

## How to rebuild these tables

Tiny corpus:

```bash
python3 examples/tfidf_toy.py --corpus examples/tiny-corpus --top 8
```

Gutenberg snapshot:

```bash
python3 scripts/rank_precomputed_tfidf.py --only carroll-alice.txt --top 12
```

To rank Alice by TF instead of tf*idf, sort `output/tf/carroll-alice.txt`
the same way the helper sorts tf*idf files. The numbers in the TF table
above were produced that way.
