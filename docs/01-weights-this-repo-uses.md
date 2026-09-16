# Weights this repo uses

The 2012 scripts implement one classic variant. Everything in `output/` is
that variant. The query desk can *also* print smoothed IDF and a BM25-lite
score, but those are teaching contrasts — they are not how the gold tables
were built.

## Term frequency

For each Gutenberg file the first Perl script accumulates raw counts, then
writes

```text
term<TAB>count / word_count
```

`word_count` is not “number of alphanumeric tokens.” It is the number of
fields produced by `split(/ +/, $line)` after the line has been collapsed,
lowercased, and stripped of punctuation. A leading space on a cleaned line
produces an empty field that **still increments** the denominator. Empty
fields are not stored as terms.

Worked fragment: the cleaned line ` alice was` splits into `("", "alice", "was")`.
`word_count` grows by 3; only `alice` and `was` enter the TF map.

On `gutenberg/carroll-alice.txt` that rule gives **26,576** denominator
tokens and **2,753** types. The gold row for `alice` is

```text
alice	0.0144867549668874
```

which is `385 / 26576`.

## Inverse document frequency

\[
\mathrm{idf}(t) = \ln\frac{N}{\mathrm{df}(t)}
\]

Natural log (`log` in Perl and in Python). **`N = 18`** in every checked-in
IDF row.

| df | idf = ln(18/df) | Meaning on this shelf |
| ---: | ---: | --- |
| 1 | 2.89037175789616 | Hapax across the eighteen texts |
| 2 | 2.19722457733622 | Two books |
| 3 | 1.79175946922805 | Three books (`alice` is in this bucket) |
| 17 | 0.05715841383995 | Missing from exactly one book |
| 18 | 0 | Present in every book |

`alice` itself has `df = 3` (Carroll, Chesterton *Thursday*, Edgeworth), so
its IDF is `ln(18/3) = 1.79175946922805`, not the hapax value. The name is
distinctive *inside* Wonderland, not unique on the shelf.

There are **221** terms with `idf = 0`. They are the function words — and a
few content words such as `angry`, `bed`, `breath`, `children` — that happen
to occur in all eighteen files. TF-IDF does not need a separate stoplist to
kill them.

The gold IDF file has **57,368** terms.

## The product

`tf*idf-product.pl` reads `output/idf.txt` and each `output/tf/*.txt`, and
writes `output/tfidf/<same-name>` as `term<TAB>tf * idf`.

Alice’s heading weight:

```text
tf(alice, Alice)  = 0.0144867549668874
idf(alice)        = 1.79175946922805
tfidf             = 0.025956813148228  (gold: 0.0259568…)
```

A row of `0` in a TF-IDF file is almost always a universal term (`idf = 0`),
not a missing count.

## What the ranking is really doing

Sorting a book’s TF-IDF file descending answers: *which terms are frequent
here and rare on the rest of the shelf?*

That is why `macb` beats `macbeth` in the Macbeth file (speaker tag + hapax
IDF), why `whale` leads Moby-Dick even though its IDF is only `ln(18/6)`
(the count is huge), and why Blake’s short *Thel* file can still surface
`thel` — short documents are not length-normalized beyond the TF denominator.

## Teaching variants (not gold)

The desk can reweight the same counts:

| Name | IDF | Use |
| --- | --- | --- |
| `classic` | `ln(N / df)` | This repo |
| `smooth` | `ln(N / (df + 1))` | Softens hapaxes; can go slightly negative |
| `sklearnish` | `ln((N + 1) / (df + 1)) + 1` | Never zero; close to scikit-learn’s default shape |
| `bm25` | Robertson–Sparck Jones `ln((N − df + 0.5) / (df + 0.5))` plus a saturated TF | Query scoring, not a drop-in replacement for the TSV product |

Use `python3 -m querydesk compare "…" --variants classic,smooth,bm25` when you
want the contrast. Gold comparison tests always use `classic` and `N = 18`.
