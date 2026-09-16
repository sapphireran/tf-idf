# Five-vignette walk-through

`examples/tiny-corpus/` is five original paragraphs, not Gutenberg
text. The token lists below are the entire documents after the
teaching tokenizer. `N = 5`, so a term that appears in one file has

```
idf = ln(5) ≈ 1.609438
```

and a term that appears in all five files has `idf = 0`.

Reproduce:

```bash
python3 examples/tfidf_toy.py --corpus examples/tiny-corpus --top 8
perl examples/tiny_tfidf.pl examples/tiny-corpus
python3 tests/test_tfidf_toy.py
```

Python and Perl agree on the printed ranking. Tables from a snapshot
run live in `examples/tiny-output/`.

## Token lists

Lengths matter because TF is `count / length`.

### `kitchen.txt` (31 tokens)

`the cook stirred the soup on the stove steam rose from the soup the
cook tasted the soup and added salt soup needs time the cook waited
while the soup simmered`

Counts that matter: `soup` 5, `cook` 3, `the` 8, everything else 1.

### `garden.txt` (26 tokens)

`the gardener watered the roses roses need sun bees visited the roses
at noon the roses bloomed by the fence the gardener smiled at the
roses`

Counts: `roses` 5, `the` 7, `gardener` 2, `at` 2, everything else 1.

### `harbor.txt` (30 tokens)

`fog wrapped the harbor a sailor tied the boat to the pier the boat
rocked in the fog harbor bells rang the sailor watched the boat drift
against the pier`

Counts: `the` 8, `boat` 3, `fog` / `harbor` / `pier` / `sailor` 2,
everything else 1.

### `workshop.txt` (25 tokens)

`the carpenter planed the oak sawdust covered the bench the oak board
became a shelf the carpenter sanded the shelf until the oak felt
smooth`

Counts: `the` 6, `oak` 3, `carpenter` / `shelf` 2, everything else 1.

### `stars.txt` (26 tokens)

`night settled on the hill a telescope tracked the stars stars flared
above the hill the telescope found a faint cluster night kept the hill
quiet`

Counts: `the` 4, `hill` 3, `night` / `stars` / `telescope` 2,
`a` 2, everything else 1.

## Shared versus unique

`the` occurs in all five files, so `df(the) = 5` and `idf(the) = 0`.
It vanishes from every ranking, which is the textbook IDF story.

`a` occurs in harbor, workshop, and stars only (`df = 3`), so it still
has a nonzero IDF, but its TF is small and it does not crack the top
8.

Content words that appear in exactly one vignette all share the same
IDF, `ln(5)`. Ranking inside a file is then decided by TF alone.

## Head scores (exact fractions)

```
tfidf = (count / |d|) * ln(5)
```

| file | term | count | \|d\| | tf*idf |
| --- | --- | ---: | ---: | ---: |
| kitchen | soup | 5 | 31 | 5/31 × ln(5) ≈ **0.259587** |
| kitchen | cook | 3 | 31 | 3/31 × ln(5) ≈ **0.155752** |
| garden | roses | 5 | 26 | 5/26 × ln(5) ≈ **0.309507** |
| garden | gardener | 2 | 26 | 2/26 × ln(5) ≈ **0.123803** |
| harbor | boat | 3 | 30 | 3/30 × ln(5) ≈ **0.160944** |
| harbor | fog | 2 | 30 | 2/30 × ln(5) ≈ **0.107296** |
| workshop | oak | 3 | 25 | 3/25 × ln(5) ≈ **0.193133** |
| workshop | carpenter | 2 | 25 | 2/25 × ln(5) ≈ **0.128755** |
| stars | hill | 3 | 26 | 3/26 × ln(5) ≈ **0.185704** |
| stars | telescope | 2 | 26 | 2/26 × ln(5) ≈ **0.123803** |

`roses` is the strongest head term in the tiny corpus: five mentions
in a 26-token file, and the word never appears elsewhere.

## The awkward second place

Garden's top 8 starts:

```
roses     0.309507
at        0.123803
gardener  0.123803
```

`at` occurs twice (`at noon`, `at the roses`) and in no other
vignette, so it ties with `gardener`. Kitchen similarly lets `and` and
`from` sit beside `salt`.

That is not a bug in the arithmetic. It is what "no stopword list"
means when N is 5. On the 18-book corpus the same mechanism promotes
`unto` and `haue`. The tiny files make the mechanism loud enough to
hear.

## How this maps back to Gutenberg

| Tiny vignette | Gutenberg analogue |
| --- | --- |
| `soup` in kitchen | `buster` in Burgess: repeated name, df = 1 |
| `roses` beating `the` | `emma` beating `the` |
| `at` tying `gardener` | `mr` ranking in Austen |
| `the` scoring 0 | `the` scoring 0 in `output/idf.txt` |
| `oak` / `oak` / `oak` | `whale` / `whales` without a stemmer (repetition without merging) |

Once these five paragraphs feel obvious, the 18-book tables in
[gutenberg-top-terms.md](gutenberg-top-terms.md) are the same story
with more words.
