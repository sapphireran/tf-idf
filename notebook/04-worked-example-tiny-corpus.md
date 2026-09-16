# 04 — Worked example on four short texts

The point of `examples/tiny_corpus/` is that every number below can
be recomputed without opening a novel. I used the `simple` tokenizer
and classic IDF. Machine-precision tables:

```bash
python3 -m tfidf demo
```

## The four documents

```
doc_cats.txt
The cat sat on the mat. The cat likes warm sun and quiet rooms.

doc_dogs.txt
The dog sat on the log. The dog likes long walks and open fields.

doc_kitchen.txt
The cook sat by the oven. Bread and soup filled the warm kitchen.

doc_stars.txt
Stars fill the quiet night. Telescopes gather faint light from distant fields.
```

## Tokens and lengths

`simple` keeps `[a-z0-9]+` after lowercasing.

| Document | Tokens in order | \|d\| |
| --- | --- | ---: |
| cats | the cat sat on the mat the cat likes warm sun and quiet rooms | 14 |
| dogs | the dog sat on the log the dog likes long walks and open fields | 14 |
| kitchen | the cook sat by the oven bread and soup filled the warm kitchen | 13 |
| stars | stars fill the quiet night telescopes gather faint light from distant fields | 12 |

Raw counts I actually use later:

| Term | cats | dogs | kitchen | stars | df |
| --- | ---: | ---: | ---: | ---: | ---: |
| the | 3 | 3 | 3 | 1 | 4 |
| sat | 1 | 1 | 1 | 0 | 3 |
| and | 1 | 1 | 1 | 0 | 3 |
| on | 1 | 1 | 0 | 0 | 2 |
| likes | 1 | 1 | 0 | 0 | 2 |
| warm | 1 | 0 | 1 | 0 | 2 |
| quiet | 1 | 0 | 0 | 1 | 2 |
| fields | 0 | 1 | 0 | 1 | 2 |
| cat | 2 | 0 | 0 | 0 | 1 |
| dog | 0 | 2 | 0 | 0 | 1 |

Every other content word (`mat`, `sun`, `rooms`, `log`, `walks`,
`cook`, `oven`, `bread`, `soup`, `kitchen`, `stars`, `telescopes`,
…) is a hapax-document term with raw count 1.

\(N = 4\).

## Classic IDF

\[
\mathrm{idf}(t) = \ln(N / n_t)
\]

| df | Terms | \(\ln(4/\mathrm{df})\) |
| ---: | --- | ---: |
| 4 | the | \(0\) |
| 3 | sat, and | \(\ln(4/3) \approx 0.287682\) |
| 2 | on, likes, warm, quiet, fields | \(\ln 2 \approx 0.693147\) |
| 1 | cat, dog, mat, telescopes, … | \(\ln 4 \approx 1.386294\) |

`the` is already dead as a weight. That is the same mechanism that
zeros `the` in the 2012 Gutenberg `output/tfidf/` tables.

## Normalized TF × IDF for `doc_cats.txt`

\(\mathrm{tf} = f / 14\).

| Term | \(f\) | tf | idf | product |
| --- | ---: | ---: | ---: | ---: |
| the | 3 | 3/14 | 0 | 0 |
| cat | 2 | 2/14 | \(\ln 4\) | \(2\ln 4 / 14 \approx 0.198042\) |
| mat | 1 | 1/14 | \(\ln 4\) | \(\ln 4 / 14 \approx 0.099021\) |
| sun | 1 | 1/14 | \(\ln 4\) | \(\approx 0.099021\) |
| rooms | 1 | 1/14 | \(\ln 4\) | \(\approx 0.099021\) |
| on | 1 | 1/14 | \(\ln 2\) | \(\approx 0.049510\) |
| likes | 1 | 1/14 | \(\ln 2\) | \(\approx 0.049510\) |
| warm | 1 | 1/14 | \(\ln 2\) | \(\approx 0.049510\) |
| quiet | 1 | 1/14 | \(\ln 2\) | \(\approx 0.049510\) |
| sat | 1 | 1/14 | \(\ln(4/3)\) | \(\approx 0.020549\) |
| and | 1 | 1/14 | \(\ln(4/3)\) | \(\approx 0.020549\) |

Highest weight: **cat**. The planted word did the job. `mat`, `sun`,
and `rooms` tie for second because they share count and rarity.
`the` is present three times and contributes nothing.

`doc_dogs.txt` is the same shape with `dog` on top.
`doc_kitchen.txt` spreads a little more: several hapax words at
\(1/13 \cdot \ln 4 \approx 0.106638\), so `bread`, `cook`, `kitchen`,
`oven`, `soup` tie.
`doc_stars.txt` is almost all hapax terms at
\(1/12 \cdot \ln 4 \approx 0.115525\), except `the` (0) and the
df=2 words `quiet` and `fields` at \(1/12 \cdot \ln 2 \approx 0.057762\).

## One query, done by hand

Query: `cat`.

Tokens: `[cat]`. Query TF (normalized) is \(1\). Query weight is
\(1 \cdot \ln 4 = \ln 4\).

Dot product with cats:

\[
(\ln 4)\cdot\frac{2\ln 4}{14} = \frac{2}{14}(\ln 4)^2 \approx 0.274653
\]

Dot product with everyone else: \(0\), because they do not contain
`cat`.

Cosine against cats needs \(\|d\|\). That is tedious by hand (eleven
non-zero coordinates). I still compute it in
`tests/test_rank.py` for the **dot** scheme, where the closed form
above is the whole test. Cosine is checked by winner-takes-the-name
assertions: `cat mat` → cats, `dog walks` → dogs,
`warm kitchen soup` → kitchen, `distant telescopes` → stars.

## The stopword query

Query: `the`.

Classic IDF is 0, so the query vector is the zero vector. Cosine is
undefined; the lab returns score `0.0` and note `empty_vector` for
every document. That is not a ranking failure. It is the formula
refusing to pretend a collection-wide word is evidence.

Under `--idf smooth` the same query gets a floor and the scores
leave zero. That is the demonstration in
[05](05-idf-smoothing-variants.md), not a better search engine.

## Why I bothered

If a later change makes `cat` lose to `doc_stars.txt` on the query
`cat mat`, the bug is in code, not in "IR is fuzzy." The shelf is
small enough that I do not get to hide behind that.
