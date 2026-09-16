# Query desk

The gold tables answer “what is distinctive *inside* each book?” A query
desk answers the other direction: **given a question, which book should I
open, and why?**

This is still personal study code. It uses the same tokenizer and, by
default, the same `ln(N / df)` weights.

## Query as a tiny document

1. Tokenize the query with the Perl-compatible rules.
2. Build normalized TF over the query’s own `word_count`.
3. Multiply by the **collection** IDF (Gutenberg’s 18-book map, or the
   field-notes map).
4. Compare that query vector to each document’s TF-IDF vector.

Default comparison is **cosine**:

\[
\cos(q,d) = \frac{\sum_t q_t d_t}{\|q\|\,\|d\|}
\]

Cosine ignores raw book length. Dot product (available as `--score dot`)
does not: *Moby-Dick* and the KJV will dominate any query that shares a
few medium-IDF words, simply because those vectors have more non-zero
coordinates.

## Attribution

For cosine, the terms that *paid* for a hit are the ones with a large
product `q_tfidf[t] * d_tfidf[t]`. `explain` prints that breakdown for the
top document (or for `--doc <file>`).

```bash
python3 -m querydesk rank "white whale pequod ahab"
python3 -m querydesk explain "white whale pequod ahab"
python3 -m querydesk explain "white whale" --doc carroll-alice.txt
```

The third command is useful when you want to see a *miss*: Alice has `white`
and almost no `whale`, so the contribution list is short and the cosine is
small.

## When BM25-lite is the better story

Classic TF-IDF cosine treats `tf = 0.2` as twice `tf = 0.1`. BM25 saturates
term frequency and then applies a length prior:

\[
\mathrm{score}(d,q) = \sum_{t \in q}
  \mathrm{idf}_{\mathrm{BM25}}(t)
  \cdot
  \frac{f_{t,d}\,(k_1+1)}{f_{t,d} + k_1\bigl(1-b+b\cdot |d|/\mathrm{avgdl}\bigr)}
\]

with `k1 = 1.2`, `b = 0.75`, and
`idf = ln((N − df + 0.5) / (df + 0.5))`.

That is a **different ranking**, not a rescaling of `output/tfidf/`. Use it
when a long book is winning only because it had room to mention the query
words once. Compare:

```bash
python3 -m querydesk compare "double toil trouble heath" --variants classic,bm25
```

## Field notes before the shelf

The four-note corpus in `examples/field-notes/` is small enough that you can
watch a query pick *exactly one* theme:

| Query | Should win |
| --- | --- |
| `cairn moraine icefall` | `glacier-cairn.txt` |
| `chase quoins tympan` | `letterpress-proof.txt` |
| `stilling datum slack` | `tide-gauge.txt` |
| `voucher blotters silica` | `herbarium-press.txt` |

```bash
python3 -m querydesk field-notes --query "chase quoins tympan"
```

Walkthrough with the actual fractions: [05-field-notes-walkthrough.md](05-field-notes-walkthrough.md).

## Flags worth knowing

| Flag | Default | Meaning |
| --- | --- | --- |
| `--score cosine\|dot` | `cosine` | Vector comparison for classic / smooth / sklearnish |
| `--variant classic\|smooth\|sklearnish` | `classic` | IDF shape for those scores |
| `--n-mode texts\|perl-last-index` | `texts` | `N = 18` vs `$#files` |
| `--from-committed` | off | Load `output/` instead of retokenizing `gutenberg/` |
| `--top K` | 8 | How many rows to print |

`--from-committed` is the fast path for `top` / `rank` when you trust the
2012 product files. `self-test` always retokenizes so it can *check* those
files.
