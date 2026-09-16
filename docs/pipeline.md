# Pipeline: from `gutenberg/` to `output/`

Two Perl scripts, run in order, produced the committed `output/` tree.
The Python package can reproduce the same four artifacts.

```
gutenberg/*.txt
        │
        ▼
tf-idf-values.pl          python3 -m tfidf_toy compute --input gutenberg
        │
        ├── output/tf/<file>     normalized tf per token per document
        ├── output/df.txt        document frequency + posting list
        └── output/idf.txt       ln(N / df) per token
                │
                ▼
tf*idf-product.pl         (included in the same Python compute)
                │
                └── output/tfidf/<file>   tf * idf per token per document
```

## Script 1: `tf-idf-values.pl`

Walks every file in `gutenberg/` whose name does not start with `.`.

For each file:

1. Tokenize as described in [`tokenization.md`](tokenization.md).
2. Count term occurrences `tf{term}`.
3. Increment a global `df{term}{filename}` set (presence, not count).
4. Write `output/tf/<filename>` as `term<TAB>count/word_count`.

After all files:

5. Set \(N\) from the `readdir` list. The committed idf table is consistent
   with **\(N = 18\)** (the number of `.txt` books), i.e. \(\ln 18\) for
   hapax-document terms.
6. Write `output/df.txt` with a header row and, per term, the df count
   plus a comma-separated list of filenames.
7. Write `output/idf.txt` as `term<TAB>ln(N/df)`.

There is no `output/` creation: the directories must already exist.
(`tfidf_toy compute` creates them.)

## Script 2: `tf*idf-product.pl`

The filename is literal: `tf` times `idf`.

1. Load every idf row into a hash.
2. For each file in `output/tf/`, multiply each term’s tf by `idf{term}`.
3. Write `output/tfidf/<filename>` as `term<TAB>product`.

The script uses `Text::CSV_XS` with a tab separator. Terms themselves
never contain tabs in this tokenizer, so the CSV parser is equivalent to
a split on the first tab.

## File formats

All tables are UTF-8-or-ASCII TSV, one record per line, **no quotes**.

### `output/tf/<doc>` and `output/tfidf/<doc>`

```
term<TAB>float
```

Rows are sorted by term (`sort keys` in Perl, Unicode code-point order
for ASCII).

### `output/idf.txt`

```
term<TAB>float
```

Sorted by term. A term that occurs in all 18 books has idf `0`.

### `output/df.txt`

```
word \t #docs it exists in \t doc names
alice	1	carroll-alice.txt,
the	18	austen-emma.txt, austen-persuasion.txt, ...
```

The header is part of the original script. Filenames in the third column
are the hash-key order from Perl, which is not sorted.

## How to read a score file without code

```bash
# highest-scoring tokens in Alice (Perl output)
awk -F'\t' '{print $2 "\t" $1}' output/tfidf/carroll-alice.txt \
  | sort -g \
  | tail -15
```

Or:

```bash
python3 -m tfidf_toy top --input gutenberg --k 15 --only carroll-alice.txt
```

## Recompute with Python

```bash
python3 -m tfidf_toy compute --input gutenberg --output output_py
```

This writes the same four artifact types under `output_py/`. The original
`output/` directory is left alone so you can diff:

```bash
python3 -m tfidf_toy diff-output --left output --right output_py
```

Small floating-point and empty-token-length differences are expected
unless you pass `--match-perl-length`. Rankings of the top few dozen
terms should match.

## Directory layout (this repo)

```
gutenberg/                 18 Project Gutenberg extracts (public domain)
output/                    committed Perl run
docs/                      math, tokens, this pipeline, worked example
examples/tiny_corpus/      3-document pencil-and-paper collection
tfidf_toy/                 Python library + CLI
tests/                     unittest coverage of the math and tokenizer
tf-idf-values.pl           original tf/df/idf writer
tf*idf-product.pl          original tf*idf writer
```
