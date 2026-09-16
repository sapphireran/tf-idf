# Snapshot: distinctive terms in the committed Gutenberg tables

These rankings were read from `output/tfidf/` with
`examples/python/inspect_gutenberg.py`. They are a snapshot of the
historical toy result, not a claim about the books as literature.

## Alice — `carroll-alice.txt`

| term | tf-idf |
| --- | ---: |
| alice | 0.025957 |
| gryphon | 0.004547 |
| dormouse | 0.004242 |
| duchess | 0.004242 |
| hatter | 0.003708 |
| turtle | 0.003169 |
| caterpillar | 0.001820 |
| rabbit | 0.001778 |

The book's own name dominates. The rest of the list is the cast.

## Moby-Dick — `melville-moby_dick.txt`

| term | tf-idf |
| --- | ---: |
| whale | 0.004943 |
| ahab | 0.004322 |
| sperm | 0.003258 |
| stubb | 0.003095 |
| queequeg | 0.002877 |
| whales | 0.002760 |
| starbuck | 0.002304 |
| pequod | 0.001650 |

Topical nouns and character names share the list. `whale` and `whales`
are separate tokens because nothing stems them.

## Hamlet — `shakespeare-hamlet.txt`

| term | tf-idf |
| --- | ---: |
| ham | 0.014075 |
| haue | 0.010224 |
| hor | 0.006806 |
| qu | 0.005843 |
| laer | 0.005655 |
| ophe | 0.005278 |
| pol | 0.004618 |
| rosin | 0.004052 |

This is the tokenizer meeting a play text. `ham` is a speaker tag,
`haue` is an old spelling, and most of the rest are abbreviated
names. See `docs/06-interpreting-scores.md`.

## Blake — `blake-poems.txt`

| term | tf-idf |
| --- | ---: |
| thel | 0.005581 |
| weep | 0.003957 |
| lyca | 0.002976 |
| thee | 0.002662 |
| vales | 0.001742 |
| oer | 0.001697 |
| lamb | 0.001461 |

A short file, so modest counts still produce visible scores. `thel`
and `lyca` are collection-unique names.

## King James Bible — `bible-kjv.txt`

| term | tf-idf |
| --- | ---: |
| unto | 0.012037 |
| israel | 0.004001 |
| saith | 0.003377 |
| thee | 0.002295 |
| david | 0.002206 |
| judah | 0.002173 |
| thou | 0.002169 |
| lord | 0.001739 |

Archaic function words stay high because they are frequent *and* less
evenly spread than `the`. `jesus` appears further down the same file;
length keeps every individual score small compared with Alice's
`alice`.

Rerun or extend the snapshot with:

```bash
python3 examples/python/inspect_gutenberg.py -n 12
```
