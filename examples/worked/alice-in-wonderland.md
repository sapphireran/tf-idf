# Reading Alice against the other 17 books

`output/tfidf/carroll-alice.txt` is alphabetical. Ranked, the top of the book is a cast list.

```
python3 examples/python/rank_terms.py \
  --tfidf-dir output/tfidf --output-root output \
  --document carroll-alice.txt --top 15
```

| Rank | Token | tf * idf | df | Why it scores |
| ---: | --- | ---: | ---: | --- |
| 1 | `alice` | 0.025957 | 3 | Frequent in this book; almost absent elsewhere |
| 2 | `gryphon` | 0.004547 | 2 | Carroll + one Milton use |
| 3 | `dormouse` | 0.004242 | 1 | Unique, but rarer inside the book than `alice` |
| 4 | `duchess` | 0.004242 | 1 | Tied with `dormouse` |
| 5 | `hatter` | 0.003708 | 3 | Shared string, still rare |
| 6 | `turtle` | 0.003169 | 4 | Mock Turtle; the word is not unique |
| 7 | `caterpillar` | 0.001820 | 3 | |
| 8 | `rabbit` | 0.001778 | 6 | Common English animal; `idf` is only `ln(18/6)` |
| 9 | `alices` | 0.001305 | 1 | `Alice's` after apostrophe stripping |
| 10 | `herself` | 0.001266 | 12 | High `tf`, weak `idf` |
| 11 | `soup` | 0.001214 | 3 | Turtle Soup |
| 12 | `mouse` | 0.001160 | 8 | |
| 13 | `hare` | 0.001102 | 7 | March Hare |
| 14 | `dodo` | 0.001075 | 2 | |
| 15 | `im` | 0.001056 | 11 | `I'm` |

## `alice` vs `dormouse`

This is the tiny-corpus `cats` vs `mice` argument on a real book.

`inspect_committed.py --token alice` shows the name in three files:

| Book | tf | tf * idf |
| --- | ---: | ---: |
| `carroll-alice.txt` | 0.014487 | 0.025957 |
| `chesterton-thursday.txt` | 1.73e-05 | 3.09e-05 |
| `edgeworth-parents.txt` | 1.20e-05 | 2.16e-05 |

So `df(alice) = 3` and `idf = ln(18/3) ≈ 1.7918`. The other two hits are stray uses of the name. They barely move the weight.

`dormouse` occurs only in Carroll, so it gets the maximum `idf ≈ 2.8904`. It still loses because its in-book `tf` is about ten times smaller than `alice`. Unique is not enough. Unique *and* frequent wins; unique *and* occasional is second tier.

`duchess` is a numerical tie with `dormouse` at 0.0042415901. Same `df`, same in-book rate in this snapshot.

## Tokens that look like bugs and are not

- **`alices`.** The possessive `Alice's` loses its apostrophe. A stemmer would have merged this with `alice` and made the name even more dominant.
- **`im`.** `I'm`. Eleven books use that contraction, so the `idf` is weak, but Alice talks enough for it to still reach the top 15.
- **`1865`.** The title line `[Alice's Adventures in Wonderland by Lewis Carroll 1865]` becomes a unique token. It does not reach the top 20; one occurrence in a 26k-token book is a small `tf`.
- **`gryphon`.** Not unique. Milton uses the creature once in *Paradise Lost*. Carroll still wins the weight by raw repetition.

## Alice is isolated in vector space

Pairwise cosine against the other 17 books, from `similarity.py --neighbors-of carroll-alice.txt`:

| Neighbor | Cosine |
| --- | ---: |
| `chesterton-brown.txt` | 0.0302 |
| `edgeworth-parents.txt` | 0.0301 |
| `bryant-stories.txt` | 0.0283 |
| `whitman-leaves.txt` | 0.0181 |
| `melville-moby_dick.txt` | 0.0152 |

The global top pair in this corpus is Hamlet–Macbeth at 0.308. Alice's nearest neighbor is an order of magnitude smaller. Her highest weights do not appear in anyone else's highest weights.

A query made of those names retrieves her immediately:

```
python3 examples/python/similarity.py \
  --tfidf-dir output/tfidf --idf output/idf.txt \
  --query "alice hatter duchess dormouse"
```

| Rank | Book | Cosine |
| ---: | --- | ---: |
| 1 | `carroll-alice.txt` | 0.5673 |
| 2 | `chesterton-brown.txt` | 0.0011 |

That is the intended use of these tables: a short string of rare, in-book-frequent tokens is already a document vector.

## What Alice does *not* tell you

The ranker never surfaces `wonderland` near the top. The word is rare in the body; it lives in the header and a handful of sentences. `tf * idf` is not a title extractor. It is a "repeated rare strings" extractor. For a children's novel whose protagonist is named every page, those strings are the cast.
