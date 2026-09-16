# Worked example: four short documents

The files in `examples/tiny-corpus/` are original teaching notes, not
Gutenberg reprints. They are small enough to tokenize on paper. Run

```bash
python3 examples/tiny_tfidf.py --check
```

to confirm the numbers below still match the scripts.

## The four documents

**tea-garden.txt**

> The rabbit drank tea in the garden. The tea was hot.
> A second cup of tea sat beside the rabbit.

**whale-ship.txt**

> The whale swam in the sea. The whale was huge.
> A ship followed the whale across the sea.

**castle-ghost.txt**

> The ghost haunted the castle. The prince saw the ghost at night.
> A cold gate opened and the ghost drifted past the prince.

**market-day.txt**

> The market sold bread and tea. A ship of bread left for the sea.
> The rabbit did not go. The prince bought bread.

Shared words (`the`, `a`, `rabbit`, `tea`, `sea`, `prince`, `ship`) are
there on purpose. The interesting part is how IDF down-weights them.

## Tokenization

The toy tokenizer is the same as `tf-idf-values.pl`: lowercase, squeeze
whitespace, delete non-alphanumeric characters, split on spaces.

`tea-garden.txt` becomes 20 tokens:

```
the rabbit drank tea in the garden the tea was hot
a second cup of tea sat beside the rabbit
```

| token | count |
| --- | ---: |
| the | 4 |
| tea | 3 |
| rabbit | 2 |
| drank, in, garden, was, hot, a, second, cup, of, sat, beside | 1 each |

`|d| = 20`, so `TF(tea) = 3/20 = 0.15` and `TF(the) = 4/20 = 0.20`.

The other three documents tokenize to 18, 23, and 23 tokens. Full strings
are printed by `python3 examples/tiny_tfidf.py --no-write`.

## Collection statistics (`N = 4`)

```
IDF(t) = ln(4 / df(t))
```

| df | IDF | Examples |
| --- | --- | --- |
| 4 | `ln(1) = 0` | `the`, `a` |
| 2 | `ln(2) ≈ 0.693147` | `tea`, `rabbit`, `sea`, `ship`, `prince`, `in`, `was`, `and`, `of` |
| 1 | `ln(4) ≈ 1.386294` | `whale`, `ghost`, `bread`, `garden`, `drank`, `castle`, ... |

`tea` is in both the garden note and the market note, so it is *not* a
max-IDF term even though it is the most frequent content word in
`tea-garden.txt`.

## Every TF-IDF weight in tea-garden.txt

```
TF-IDF(t, tea-garden) = TF(t) * IDF(t)
```

| term | count | TF | df | IDF | TF-IDF |
| --- | ---: | ---: | ---: | ---: | ---: |
| tea | 3 | 0.15 | 2 | 0.693147 | **0.103972** |
| rabbit | 2 | 0.10 | 2 | 0.693147 | 0.069315 |
| drank | 1 | 0.05 | 1 | 1.386294 | 0.069315 |
| garden | 1 | 0.05 | 1 | 1.386294 | 0.069315 |
| hot | 1 | 0.05 | 1 | 1.386294 | 0.069315 |
| second | 1 | 0.05 | 1 | 1.386294 | 0.069315 |
| cup | 1 | 0.05 | 1 | 1.386294 | 0.069315 |
| sat | 1 | 0.05 | 1 | 1.386294 | 0.069315 |
| beside | 1 | 0.05 | 1 | 1.386294 | 0.069315 |
| in | 1 | 0.05 | 2 | 0.693147 | 0.034657 |
| was | 1 | 0.05 | 2 | 0.693147 | 0.034657 |
| of | 1 | 0.05 | 2 | 0.693147 | 0.034657 |
| the | 4 | 0.20 | 4 | 0 | 0 |
| a | 1 | 0.05 | 4 | 0 | 0 |

`tea` wins because three mentions beat a single unique mention once IDF is
applied. `rabbit` (two mentions, shared with the market) ties the unique
singletons. `the` is the most common token and contributes nothing.

## Top term in each document

| document | top term | TF | IDF | TF-IDF |
| --- | --- | ---: | ---: | ---: |
| tea-garden.txt | tea | 0.15 | 0.693147 | 0.103972 |
| whale-ship.txt | whale | 0.166667 | 1.386294 | 0.231049 |
| castle-ghost.txt | ghost | 0.130435 | 1.386294 | 0.180821 |
| market-day.txt | bread | 0.130435 | 1.386294 | 0.180821 |

`whale` outscores `tea` even though both notes repeat their theme word
three times. The whale is unique to one document (`df = 1`); the tea is
not (`df = 2`). That is IDF doing the work the stopword list would
otherwise be asked to do.

## Querying the toy shelf

After `python3 examples/tiny_tfidf.py` writes `examples/tiny-output/`:

```bash
python3 examples/query_documents.py --dir examples/tiny-output/tfidf tea rabbit
python3 examples/query_documents.py --dir examples/tiny-output/tfidf whale ship
python3 examples/query_documents.py --dir examples/tiny-output/tfidf ghost castle
python3 examples/query_documents.py --dir examples/tiny-output/tfidf bread market
```

Each query is a sum of the per-document weights for those terms. `tea` +
`rabbit` favors `tea-garden.txt`; `bread` is unique and heavy enough that
`market-day.txt` still wins a `tea`-flavored grocery query.

## Regenerating the tables

```bash
python3 examples/tiny_tfidf.py
```

writes `examples/tiny-output/df.txt`, `idf.txt`, `tf/`, and `tfidf/` in the
same tab-separated shape as the Gutenberg `output/` directory. The
`--check` flag re-reads the four files above and asserts the top-term
scores in this note.
