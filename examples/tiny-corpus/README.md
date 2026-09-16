# Tiny corpus: a worked TF-IDF example

Four original paragraphs. No Gutenberg text. The numbers below were
produced by [run_tfidf.py](run_tfidf.py), which uses the same
tokenization and the same `ln(N / df)` IDF as the Perl scripts, with
one deliberate difference: **N is the number of processed documents
(4)**, not `$#files` after `readdir`.

```bash
python3 examples/tiny-corpus/run_tfidf.py --check
```

## The four documents

**cats.txt** — a cat named Miso misses a moth, then watches it.

**bread.txt** — a baker feeds starter, shapes dough, and cools bread.

**stars.txt** — a telescope finds Saturn; two meteors cross the sky.

**garden.txt** — tomato vines, basil, a salad, a sandwich.

Each file is 36 or 37 tokens after the Perl-style tokenizer. That is
small enough to count by hand and large enough for a few words to
repeat.

## Tokenization (same rules as `tf-idf-values.pl`)

For every line:

1. Strip the end-of-line character.
2. Collapse runs of whitespace to a single space.
3. Lowercase.
4. Delete every character that is not `[a-zA-Z0-9]` or whitespace.
5. Split on one or more spaces.
6. Increment `word_count` for every token, including empty ones.
7. Store only non-empty tokens in TF and DF.

Periods and commas disappear. A hyphen would glue two words together
(`moth-shadow` → `mothshadow`); these texts avoid hyphens so the
hand count stays honest. The Gutenberg run is full of glued tokens —
see [docs/04-design-notes.md](../../docs/04-design-notes.md).

## Term frequency

Normalized TF is `count / word_count` for that file.

| document | tokens | term | count | TF |
| --- | ---: | --- | ---: | ---: |
| cats.txt | 36 | moth | 4 | 4/36 = 0.111111 |
| cats.txt | 36 | miso | 3 | 3/36 = 0.083333 |
| cats.txt | 36 | cat | 2 | 2/36 = 0.055556 |
| cats.txt | 36 | the | 7 | 7/36 = 0.194444 |
| garden.txt | 37 | tomato | 4 | 4/37 = 0.108108 |
| stars.txt | 36 | saturn | 3 | 3/36 = 0.083333 |
| stars.txt | 36 | telescope | 3 | 3/36 = 0.083333 |
| bread.txt | 37 | baker | 2 | 2/37 = 0.054054 |

`the` is the most common word in `cats.txt`, but it is about to be
wiped out by IDF.

## Inverse document frequency

`N = 4`. IDF is the natural log of `N / df`. No add-one. A term that
appears in every document scores exactly 0.

| term | df | documents | IDF |
| --- | ---: | --- | ---: |
| moth | 1 | cats | ln(4/1) = 1.386294 |
| miso | 1 | cats | 1.386294 |
| tomato | 1 | garden | 1.386294 |
| saturn | 1 | stars | 1.386294 |
| baker | 1 | bread | 1.386294 |
| waits | 2 | cats, bread | ln(4/2) = 0.693147 |
| and | 3 | bread, cats, garden | ln(4/3) = 0.287682 |
| the | 4 | all four | ln(4/4) = 0 |
| a | 4 | all four | 0 |
| on | 4 | all four | 0 |

`the` has the highest TF in the cat note and the lowest possible IDF.
That is the whole trick.

## TF × IDF

| document | term | TF | IDF | TF-IDF |
| --- | --- | ---: | ---: | ---: |
| cats.txt | moth | 0.111111 | 1.386294 | **0.154033** |
| cats.txt | miso | 0.083333 | 1.386294 | **0.115525** |
| cats.txt | cat | 0.055556 | 1.386294 | **0.077016** |
| cats.txt | the | 0.194444 | 0 | **0** |
| garden.txt | tomato | 0.108108 | 1.386294 | **0.149870** |
| garden.txt | basil | 0.081081 | 1.386294 | **0.112402** |
| stars.txt | saturn | 0.083333 | 1.386294 | **0.115525** |
| stars.txt | telescope | 0.083333 | 1.386294 | **0.115525** |
| stars.txt | meteor | 0.055556 | 1.386294 | **0.077016** |
| bread.txt | baker | 0.054054 | 1.386294 | **0.074935** |
| bread.txt | bread | 0.054054 | 1.386294 | **0.074935** |
| bread.txt | dough | 0.054054 | 1.386294 | **0.074935** |

`--check` reasserts the moth identity:

```text
tf=0.111111 * idf=1.386294 = 0.154033
```

## How to read the ranking

Within one document, a high score means "this word is common *here*
and rare *elsewhere*." Across documents, compare scores only as a
rough signal: the four files are almost the same length, so the
values sit on a similar scale. On the Gutenberg corpus the files
range from 38 KB (Blake) to 4.3 MB (KJV Bible), so a raw TF-IDF
number from `blake-poems.txt` is not comparable to one from
`bible-kjv.txt` without thinking about length.

Tied scores are normal. In `bread.txt`, `baker`, `bread`, `dough`,
and `into` all occur twice and nowhere else, so they share
0.074935. Alphabetical order is just a tie-break.

## Snapshots

`expected/` uses the same layout as the repo-level `output/`
directory:

```text
expected/df.txt
expected/idf.txt
expected/tf/<document>
expected/tfidf/<document>
```

Refresh them after editing a text:

```bash
python3 examples/tiny-corpus/run_tfidf.py --write-expected --check
```

## Mapping back to the Perl scripts

| Tiny runner | Perl |
| --- | --- |
| `read_document()` TF loop | first half of `tf-idf-values.pl` |
| `idf[term] = log(n / df)` | `log($n/($#vals+1))` in the same file |
| `tf * idf` per term | `tf*idf-product.pl` |
| printed ranking | not in Perl; use `examples/rank_terms.py` on `output/` |
