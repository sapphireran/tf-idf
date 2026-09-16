# Hand calculation on the four-document corpus

Corpus: [`tiny-corpus/docs/`](tiny-corpus/docs/).
Formulas: [`../docs/tf-idf-explained.md`](../docs/tf-idf-explained.md).
Tokenizer: lowercase, strip non-alphanumerics, split on spaces. These four
files have no leftover empty tokens, so `tokens(d)` equals the kept-word count.

Natural log, `N = 4`:

```
ln(4/1) = ln(4) ≈ 1.38629436112
ln(4/2) = ln(2) ≈ 0.69314718056
ln(4/3)         ≈ 0.28768207245
ln(4/4) = ln(1) = 0
```

The Python scorer reprints these values:

```bash
python3 examples/tiny-corpus/compute_tfidf.py --verify
```

## The documents, already tokenized

### `apple-orchard.txt` — 20 tokens

> The apple trees bloom in the orchard.
> Sweet apple cider drips from the press.
> Blossom petals cover the orchard grass.

```
the apple trees bloom in the orchard
sweet apple cider drips from the press
blossom petals cover the orchard grass
```

Counts: `the` 4, `apple` 2, `orchard` 2; every other kept term 1.

### `ocean-voyage.txt` — 18 tokens

> The whale dives under the ship.
> Salt spray hits the ocean deck.
> The ship follows the whale north.

Counts: `the` 5, `whale` 2, `ship` 2; others 1.

### `city-market.txt` — 21 tokens

> The city market sells apple tarts.
> A stall in the market crowds the street.
> City vendors shout near the apple stall.

Counts: `the` 4, `apple` 2, `city` 2, `market` 2, `stall` 2; others 1
(including `a`).

### `night-garden.txt` — 19 tokens

> Moon light falls on the garden path.
> Night blossom opens in the garden.
> The moon watches the quiet night.

Counts: `the` 4, `moon` 2, `garden` 2, `night` 2; others 1 (including
`blossom`).

## Document frequency

Only a handful of terms appear in more than one file. Everything else is
`df = 1`.

| Term | df | Documents | idf |
| --- | ---: | --- | ---: |
| `the` | 4 | all four | 0 |
| `in` | 3 | orchard, market, garden | 0.28768207245 |
| `apple` | 2 | orchard, market | 0.69314718056 |
| `blossom` | 2 | orchard, garden | 0.69314718056 |
| every other term | 1 | one file | 1.38629436112 |

That table is the whole IDF story for this corpus.

## TF and TF-IDF for `apple-orchard`

`tokens = 20`.

| Term | count | tf = count/20 | df | idf | tfidf |
| --- | ---: | ---: | ---: | ---: | ---: |
| `the` | 4 | 0.20 | 4 | 0 | **0** |
| `apple` | 2 | 0.10 | 2 | 0.69314718056 | **0.06931471806** |
| `orchard` | 2 | 0.10 | 1 | 1.38629436112 | **0.13862943611** |
| `blossom` | 1 | 0.05 | 2 | 0.69314718056 | **0.03465735903** |
| `in` | 1 | 0.05 | 3 | 0.28768207245 | **0.01438410362** |
| `bloom`, `cider`, `trees`, … | 1 | 0.05 | 1 | 1.38629436112 | **0.06931471806** |

`apple` and `orchard` have the **same TF**. IDF doubles `orchard` because the
market never says “orchard” and does say “apple.” `the` is the most frequent
token and still scores zero. `blossom` is penalized for also appearing in the
garden document.

Ranked exclusive content words for this file (ties broken alphabetically in
the scorer's rank view):

1. `orchard` — 0.13862944
2. a large tie at 0.06931472: `apple`, `bloom`, `cider`, `cover`, `drips`,
   `from`, `grass`, `petals`, `press`, `sweet`, `trees`
3. `blossom` — 0.03465736
4. `in` — 0.01438410
5. `the` — 0

`apple` sits in the tie band, not at the top. That is the intended lesson.

## `ocean-voyage` (18 tokens)

| Term | count | tf | df | tfidf |
| --- | ---: | ---: | ---: | ---: |
| `the` | 5 | 5/18 ≈ 0.277778 | 4 | 0 |
| `ship` | 2 | 2/18 ≈ 0.111111 | 1 | **0.15403271** |
| `whale` | 2 | 2/18 ≈ 0.111111 | 1 | **0.15403271** |
| any singleton (`ocean`, `salt`, …) | 1 | 1/18 ≈ 0.055556 | 1 | **0.07701635** |

No term from this file appears in the other three (except `the`), so IDF does
not split `ship` from `whale`. Frequency inside the file is the only ranking
signal left.

## `city-market` (21 tokens)

| Term | count | tf | df | tfidf |
| --- | ---: | ---: | ---: | ---: |
| `the` | 4 | 4/21 ≈ 0.190476 | 4 | 0 |
| `city` | 2 | 2/21 ≈ 0.095238 | 1 | **0.13202803** |
| `market` | 2 | 2/21 ≈ 0.095238 | 1 | **0.13202803** |
| `stall` | 2 | 2/21 ≈ 0.095238 | 1 | **0.13202803** |
| `apple` | 2 | 2/21 ≈ 0.095238 | 2 | **0.06601402** |
| `a` | 1 | 1/21 ≈ 0.047619 | 1 | **0.06601402** |
| `in` | 1 | 1/21 ≈ 0.047619 | 3 | **0.01369915** |

`apple` is as frequent as `city` / `market` / `stall` but loses half its weight
to the orchard document. `a` is a function word that happens to appear in only
this file (`A stall…` after lowercasing), so it gets the full singleton IDF.
That is a real TF-IDF footgun on tiny corpora: **accidental hapax function
words look “distinctive.”**

## `night-garden` (19 tokens)

| Term | count | tf | df | tfidf |
| --- | ---: | ---: | ---: | ---: |
| `the` | 4 | 4/19 ≈ 0.210526 | 4 | 0 |
| `garden` | 2 | 2/19 ≈ 0.105263 | 1 | **0.14592572** |
| `moon` | 2 | 2/19 ≈ 0.105263 | 1 | **0.14592572** |
| `night` | 2 | 2/19 ≈ 0.105263 | 1 | **0.14592572** |
| singleton (`falls`, `light`, …) | 1 | 1/19 ≈ 0.052632 | 1 | **0.07296286** |
| `blossom` | 1 | 1/19 ≈ 0.052632 | 2 | **0.03648143** |
| `in` | 1 | 1/19 ≈ 0.052632 | 3 | **0.01514116** |

`blossom` is the shared seasonal word; it ranks below the exclusive night-and-
garden terms even though its in-document TF matches `falls` or `path`.

## Cross-document comparison (do this carefully)

`whale` in the voyage file scores `0.154`; `orchard` scores `0.139`. Those
magnitudes are **not** “whale is more distinctive than orchard in the universe.”
They are TF-IDF inside different-length documents (18 vs 20 tokens) against the
same 4-document IDF table. See the ranking-vs-magnitude note in
[`../docs/tf-idf-explained.md`](../docs/tf-idf-explained.md).

## Mapping this back to Gutenberg

The same four effects show up in `output/`:

| Tiny-corpus effect | Gutenberg analogue |
| --- | --- |
| `the` → 0 | `the` / `and` / `of` → 0 in every `output/tfidf/` file |
| `orchard` beats same-TF `apple` | `ahab` nearly catches more-frequent `whale` because `df(ahab)=2 < df(whale)=6` |
| hapax `a` looks important | `ebook` in *The Ball and the Cross* |
| shared `blossom` shrinks | `anne` is weaker than `elliot` in *Persuasion* (`df` 6 vs 1) |

Continue with [`gutenberg-top-terms.md`](gutenberg-top-terms.md) once this
arithmetic feels boring.
