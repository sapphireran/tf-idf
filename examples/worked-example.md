# Worked example (four tiny documents)

This is the same collection as [`toy-corpus/`](toy-corpus/). Every number below can be reproduced with:

```bash
python3 examples/run_toy_example.py
python3 examples/test_toy_example.py
```

The tokenizer does not have to do anything interesting here: the files are already lowercase, one line, no punctuation. Each whitespace-separated word is a token. There are no empty fields, so the Perl-faithful denominator and a “non-empty only” denominator agree.

## The documents

| File | Text | Tokens \(n_d\) |
| --- | --- | --- |
| `cats.txt` | the cat sat on the mat the cat likes fish | 10 |
| `dogs.txt` | the dog sat on the log the dog likes bones | 10 |
| `space.txt` | rockets fly to the moon astronauts like space | 8 |
| `pets.txt` | the cat and the dog play on the mat | 9 |

\(N = 4\).

## Term frequency

\[
\mathrm{tf}(t, d) = \mathrm{count}(t, d) / n_d
\]

**cats.txt** — `the` appears 3 times, `cat` twice, everything else once:

| term | count | tf |
| --- | --- | --- |
| the | 3 | 3/10 = 0.3 |
| cat | 2 | 2/10 = 0.2 |
| sat, on, mat, likes, fish | 1 each | 0.1 |

**dogs.txt** — same shape: `the` 0.3, `dog` 0.2, `sat`/`on`/`log`/`likes`/`bones` 0.1.

**space.txt** — eight distinct tokens, each 1/8 = 0.125.

**pets.txt** — `the` appears 3 times in 9 tokens:

| term | count | tf |
| --- | --- | --- |
| the | 3 | 1/3 ≈ 0.333333 |
| cat, and, dog, play, on, mat | 1 each | 1/9 ≈ 0.111111 |

## Document frequency and idf

\[
\mathrm{df}(t) = \lvert \{ d : t \in d \} \rvert
\qquad
\mathrm{idf}(t) = \ln(N / \mathrm{df}(t)) = \ln(4 / \mathrm{df}(t))
\]

Natural log, same as Perl’s `log`.

| term | documents | df | idf |
| --- | --- | --- | --- |
| the | cats, dogs, space, pets | 4 | ln(1) = **0** |
| on | cats, dogs, pets | 3 | ln(4/3) ≈ **0.287682** |
| cat, sat, mat, likes, dog | two files each | 2 | ln(2) ≈ **0.693147** |
| fish, log, bones, rockets, fly, to, moon, astronauts, like, space, and, play | one file each | 1 | ln(4) ≈ **1.386294** |

`likes` (cats + dogs) is not the same term as `like` (space). The toy does not stem.

## tf-idf

\[
\mathrm{tfidf}(t, d) = \mathrm{tf}(t, d) \times \mathrm{idf}(t)
\]

### cats.txt

| term | tf | idf | tf-idf |
| --- | --- | --- | --- |
| the | 0.3 | 0 | **0** |
| on | 0.1 | 0.287682 | 0.028768 |
| sat / mat / likes | 0.1 | 0.693147 | 0.069315 |
| **cat** | 0.2 | 0.693147 | **0.138629** |
| **fish** | 0.1 | 1.386294 | **0.138629** |

`cat` and `fish` tie for first. Frequency (`cat` twice) and rarity (`fish` only here) balance. `the` is gone.

### dogs.txt

| term | tf-idf |
| --- | --- |
| the | 0 |
| on | 0.028768 |
| sat / likes | 0.069315 |
| **dog / log / bones** | **0.138629** |

`dog` (tf 0.2, idf ln 2) ties `log` and `bones` (tf 0.1, idf ln 4). Same arithmetic as `cat` vs `fish`.

### space.txt

| term | tf-idf |
| --- | --- |
| the | 0 |
| every other token | 0.125 × ln(4) ≈ **0.173287** |

A document whose content words are all unique in the collection gets a flat high ranking. That is correct and slightly boring — idf cannot break ties when df is 1 for every remaining term.

### pets.txt

| term | tf-idf |
| --- | --- |
| the | 0 |
| on | (1/9) × ln(4/3) ≈ 0.031965 |
| cat / dog / mat | (1/9) × ln(2) ≈ 0.077016 |
| **and / play** | (1/9) × ln(4) ≈ **0.154033** |

`and` tying `play` is the teaching bruise: with no stopword list, a function word that happens to be missing from the other three files looks “distinctive.” idf only knows document counts, not parts of speech. A larger, messier collection (the Gutenberg pocket corpus) sends `and` to idf 0 because every book uses it.

## What to notice

1. **Zeros are successes.** `the` really should not identify any of these files.
2. **Ties are information.** They tell you the two factors traded off exactly (`0.2 × ln 2 = 0.1 × ln 4`).
3. **Collection design is the model.** Add a fifth document that mentions `fish` and `bones` and the pet-file winners move.
4. **This is the same product as the Perl scripts.** The only intentional difference is that \(N\) is “files we parsed” (4), not `$#files` after `readdir`.

Open [../docs/tf-idf-explained.md](../docs/tf-idf-explained.md) if you want the same ideas without the arithmetic, then rank a real Gutenberg file with `examples/top_terms.py`.
