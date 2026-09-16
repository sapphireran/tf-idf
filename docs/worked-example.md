# Worked example: three short documents

The files in [`examples/tiny_corpus/`](../examples/tiny_corpus/) are small
enough that every tf-idf value can be computed by hand. Run the same
numbers with:

```bash
python3 -m tfidf_toy demo
```

The unittest `tests/test_tiny_corpus.py` pins the exact floats below.

## Documents

**`alice.txt`**

```
Alice chased the rabbit. The rabbit was late.
```

**`whale.txt`**

```
The whale struck the ship. The ship was late.
```

**`hamlet.txt`**

```
Hamlet saw the ghost. The ghost was late.
```

After tokenization (lowercase, strip punctuation, split on spaces):

| document | tokens | \( |d| \) |
| --- | --- | --- |
| alice | alice, chased, the, rabbit, the, rabbit, was, late | 8 |
| whale | the, whale, struck, the, ship, the, ship, was, late | 9 |
| hamlet | hamlet, saw, the, ghost, the, ghost, was, late | 8 |

## Document frequency

\(N = 3\). Presence, not raw count, matters for df.

| term | df | appears in |
| --- | --- | --- |
| alice | 1 | alice |
| chased | 1 | alice |
| rabbit | 1 | alice |
| whale | 1 | whale |
| struck | 1 | whale |
| ship | 1 | whale |
| hamlet | 1 | hamlet |
| saw | 1 | hamlet |
| ghost | 1 | hamlet |
| the | 3 | all |
| was | 3 | all |
| late | 3 | all |

## Inverse document frequency

\[
\mathrm{idf}(t) = \ln\frac{3}{\mathrm{df}(t)}
\]

\(\ln 3 \approx 1.0986122886681098\). \(\ln 1 = 0\).

| term | idf |
| --- | --- |
| any df=1 term | \(\ln 3 \approx 1.0986122886681098\) |
| `the`, `was`, `late` | \(\ln(3/3) = 0\) |

Shared glue words are **exactly** zeroed. No stoplist required.

## Term frequency and tf-idf

### alice.txt

| term | count | tf = count/8 | tf-idf |
| --- | --- | --- | --- |
| alice | 1 | 0.125 | 0.13732653608351372 |
| chased | 1 | 0.125 | 0.13732653608351372 |
| rabbit | 2 | 0.25 | 0.27465307216702745 |
| the | 2 | 0.25 | 0.0 |
| was | 1 | 0.125 | 0.0 |
| late | 1 | 0.125 | 0.0 |

**Top distinctive token:** `rabbit` (said twice, and only in this
document). `alice` and `chased` tie for second. `the` is common in the
sentence but disappears from the ranking.

### whale.txt

| term | count | tf = count/9 | tf-idf |
| --- | --- | --- | --- |
| whale | 1 | 1/9 ≈ 0.111111 | 0.12206803207423442 |
| struck | 1 | 1/9 | 0.12206803207423442 |
| ship | 2 | 2/9 ≈ 0.222222 | 0.24413606414846885 |
| the | 3 | 3/9 | 0.0 |
| was | 1 | 1/9 | 0.0 |
| late | 1 | 1/9 | 0.0 |

**Top distinctive token:** `ship`. The extra `the` in this slightly longer
document does not help; its idf is zero. Length normalization means a
single `whale` scores a little lower than a single `alice` (9 tokens vs 8).

### hamlet.txt

| term | count | tf = count/8 | tf-idf |
| --- | --- | --- | --- |
| hamlet | 1 | 0.125 | 0.13732653608351372 |
| saw | 1 | 0.125 | 0.13732653608351372 |
| ghost | 2 | 0.25 | 0.27465307216702745 |
| the | 2 | 0.25 | 0.0 |
| was | 1 | 0.125 | 0.0 |
| late | 1 | 0.125 | 0.0 |

**Top distinctive token:** `ghost`.

## What this example is meant to show

1. **Contrast beats raw frequency.** `the` is the most common token in
   `whale.txt` and still scores 0.
2. **Repeating a rare word matters.** `rabbit` / `ship` / `ghost` beat the
   character names because they occur twice.
3. **Length matters.** The same single occurrence is worth more in a
   shorter document (`alice` vs `whale`).
4. **The ranking is collection-relative.** If you added a fourth document
   that also mentioned a ghost, `ghost`’s idf would drop for everyone.

## Smoothed idf on the same tokens

With `--idf smooth` the Python CLI uses

\[
\ln\frac{N+1}{\mathrm{df}+1}+1
\]

Then `the` is no longer zero:

\[
\ln\frac{4}{4}+1 = 1
\]

and a one-document term is \(\ln(4/2)+1 = \ln 2 + 1 \approx 1.693147\).
The ranking *inside* one of these three files stays similar, but you lose
the sharp “appears everywhere → drop it” behavior that the original Perl
formulas were written to demonstrate. The demo command prints both
variants.
