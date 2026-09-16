# Worked example

This page repeats the arithmetic for `examples/toy-corpus/` using the same tokenization as `tf-idf-values.pl` and `N = 4` processed documents. After `perl examples/toy-tfidf.pl`, the printed ranks and `examples/toy-output/` must match these figures (within ordinary floating-point noise).

## Collection

| File | Tokens (`word_count`) | Unique tokens | Theme |
| --- | ---: | ---: | --- |
| `cats.txt` | 100 | 59 | calico cat, moths, lantern |
| `harbor.txt` | 95 | 65 | schooner, tide, lighthouse |
| `bakery.txt` | 91 | 56 | sourdough, rye, oven |
| `observatory.txt` | 94 | 55 | comet, nebula, telescope |

Vocabulary size: 197 tokens. Shared English (`the`, `a`) appears in all four files.

## Tokenization reminder

`Miso` → `miso`. `comet's` would become `comets` if it appeared; the observatory text uses `comet tail` instead. Punctuation is deleted before the split, so `dawn.` and `dawn` are the same token.

## IDF for a few tokens

```text
idf(t) = ln(N / df(t))     N = 4
ln(4/1) = 1.38629436112
ln(4/2) = 0.69314718056
ln(4/4) = 0
```

| Token | df | Documents | idf |
| --- | ---: | --- | ---: |
| `cat` | 1 | cats | 1.386294 |
| `lantern` | 1 | cats | 1.386294 |
| `schooner` | 1 | harbor | 1.386294 |
| `rye` | 1 | bakery | 1.386294 |
| `comet` | 1 | observatory | 1.386294 |
| `nebula` | 1 | observatory | 1.386294 |
| `wind` | 2 | harbor, observatory | 0.693147 |
| `would` | 2 | harbor, observatory | 0.693147 |
| `the` | 4 | all four | 0 |
| `a` | 4 | all four | 0 |

## Hand calculation: `cat` in `cats.txt`

`cat` occurs five times in 100 tokens (the three `calico cat` phrases plus `The cat crouched` and `The cat only watched`).

```text
TF(cat, cats)     = 5 / 100 = 0.05
idf(cat)          = ln(4/1) = 1.38629436112
tfidf(cat, cats)  = 0.05 × 1.38629436112 = 0.069314718056
```

That is the largest score in `cats.txt`. `lantern` occurs four times:

```text
TF(lantern, cats)    = 4 / 100 = 0.04
tfidf(lantern, cats) = 0.04 × 1.38629436112 = 0.055451774445
```

`moths`, `moth`, `miso`, `hedge`, and `calico` each occur three times, so they tie at `0.03 × 1.38629436112 = 0.041588830834`.

## Contrast: `the` in the same file

`the` is frequent in `cats.txt` (and in every other file). Frequency does not save it:

```text
idf(the) = ln(4/4) = 0
tfidf(the, cats) = TF(the, cats) × 0 = 0
```

The TF table still stores a large probability for `the`. The TF-IDF table stores `0`. `examples/lookup-term.pl` on the toy output shows both sides.

## Shared-but-not-universal: `wind`

`wind` appears once in `harbor.txt` (95 tokens) and once in `observatory.txt` (94 tokens).

```text
idf(wind) = ln(4/2) = 0.69314718056

tfidf(wind, harbor)      = (1/95) × 0.69314718056 = 0.007296286111
tfidf(wind, observatory) = (1/94) × 0.69314718056 = 0.007373906176
```

A word that is unique to one file and appears only once scores `1.386294 / word_count` (about `0.0146` in the harbor file). `wind` ranks below those hapax terms because IDF is half as large. That is the whole point of the inverse document frequency term.

## Top of each toy document

These ranks are what `toy-tfidf.pl --top 6` should print:

**cats.txt** — cat, lantern, then the five-way tie moths / moth / miso / hedge / calico.

**harbor.txt** — schooner (3), then tide / lighthouse / kelp / harbor / crew (2 each).

**bakery.txt** — rye (4), then sourdough / loaves / baker (3 each).

**observatory.txt** — nebula and comet (4 each), then telescope and dome (3 each).

If a rerun disagrees, check that you pointed `--corpus` at `examples/toy-corpus` and that no extra files landed in that directory (extra files change `N` and every IDF).

## Mapping back to Gutenberg

The same arithmetic produced `alice ≈ 0.026` in the committed `output/tfidf/carroll-alice.txt`: a large TF for a name that appears in only a few of the 18 files. `the` is zero there for the same reason it is zero here. The toy corpus is small enough to count; the Gutenberg snapshot is the same experiment at collection scale.
