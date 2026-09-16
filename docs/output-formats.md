# Output file formats

Every artifact in this project is UTF-8 (in practice ASCII) text with
tab-separated columns and no quoting. The original Perl product script
parses the same files with `Text::CSV_XS` configured for tabs.

## Directory map

```
output/
  tf/<name>.txt      one file per input document
  tfidf/<name>.txt   one file per input document
  df.txt             collection document frequency
  idf.txt            collection inverse document frequency
  df-sorted.txt      extra snapshot; same idea as df.txt, different order
```

The teaching Python writes the first four. It does not write
`df-sorted.txt`.

## `output/tf/<file>`

| Column | Type | Meaning |
| --- | --- | --- |
| 1 | string | token after the shared tokenizer |
| 2 | float | `count(t, d) / words(d)` |

- No header row.
- One term per line.
- Terms sorted lexicographically (`sort keys %tf` in Perl,
  `sorted(tf)` in Python).
- A term that never occurs in that document is omitted, not written
  as zero.

Example from the snapshot (`carroll-alice.txt`):

```
a	0.0235927152317881
alice	0.0144867559588874
```

`a` is the larger TF. It will not survive the IDF multiply.

## `output/idf.txt`

| Column | Type | Meaning |
| --- | --- | --- |
| 1 | string | token |
| 2 | float | `ln(N / df(t))` with `N = 18` in the snapshot |

- No header row.
- Terms sorted lexicographically.
- Collection-wide terms (`df = 18`) are present with value `0`.
- The maximum value in the snapshot is `ln(18) ≈ 2.89037175789616`.

```
a	0
alice	1.79175946922805
ahab	2.19722457733622
```

`alice` at `1.79175946922805` is `ln(6)`, so `df(alice) = 18 / 6 = 3`.
The name appears in three of the 18 files, not only in Carroll.

`ahab` at `2.19722457733622` is `ln(9)`, so `df(ahab) = 2`.

## `output/df.txt`

| Column | Type | Meaning |
| --- | --- | --- |
| 1 | string | token |
| 2 | integer | `df(t)` |
| 3 | string | comma-separated filenames, trailing comma and space |

The first line is a header:

```
word \t #docs it exists in \t doc names
```

That header is **not** a term. Do not feed `df.txt` to a generic TSV
ranker without skipping it.

Filename order in column 3 is hash-iteration order from the original
Perl run. Do not treat it as alphabetical or chronological.

## `output/tfidf/<file>`

| Column | Type | Meaning |
| --- | --- | --- |
| 1 | string | token |
| 2 | float | `tf(t, d) * idf(t)` |

Same sorting and omission rules as the TF files. Terms with TF-IDF
`0` (because `idf = 0`) are still written in the snapshot:

```
a	0
alice	0.02595678...
```

The teaching Python keeps the same behavior: a term that occurred in
the document is written even when the product is zero.

## `output/df-sorted.txt`

A large extra snapshot from the original project. It is not produced
by either Perl script in this checkout and is not consumed by
`tf*idf-product.pl`. Treat it as leftover study output.

## Ranking the scores

The TSV files are alphabetized, not ranked. To see the interesting
end of a document:

```bash
python3 examples/python/top_terms.py output/tfidf --top 12
```

`top_terms.py` also accepts a single file:

```bash
python3 examples/python/top_terms.py output/tfidf/melville-moby_dick.txt --top 12
```

Sort key: numeric column 2, descending. Ties keep lexicographic order
so the listing is stable.

## Floating-point comparison

Do not expect byte-identical floats between Perl and Python. Tests in
`tests/` compare teaching-pipeline values with an absolute tolerance
(`1e-12` on the tiny corpus, where counts are small integers). When
comparing against `output/`, compare rankings and reconstructed
`df = round(N / exp(idf))` rather than string equality.

## Reconstructing DF from IDF

Because `idf = ln(N / df)` and `N = 18`:

```
df(t) = N / exp(idf(t))
```

That reconstruction is exact for the snapshot values listed in
[interpreting-results.md](interpreting-results.md) (`alice` → 3,
`ahab` → 2, `whale` → 6).
