# Pipeline

Two scripts, three output directories, no configuration file. Everything is relative to the repository root.

```text
gutenberg/*.txt          raw documents
        │
        ▼
tf-idf-values.pl
        │
        ├── output/tf/<same-filename>     term → tf
        ├── output/df.txt                 term → df + file list
        ├── output/df-sorted.txt          same idea, convenience sort (committed extra)
        └── output/idf.txt                term → idf
                │
                ▼
        tf*idf-product.pl
                │
                └── output/tfidf/<same-filename>   term → tf * idf
```

## Scripts

### 1. `tf-idf-values.pl`

Opens every non-dot file in `gutenberg/`. For each file it:

1. Reads the whole text into memory.
2. Strips end-of-line characters, collapses horizontal/vertical whitespace to a single space, lowercases, and deletes anything that is not `A-Z`, `a-z`, `0-9`, or whitespace.
3. Splits on one or more spaces.
4. Tallies `tf` for that file and records that the term was seen in that filename (`df` is a set of filenames, not a raw count of occurrences).
5. Writes `output/tf/<filename>` as `term<TAB>tf`, terms in alphabetical order.

After the loop it writes:

- `output/df.txt` — header row, then `term`, document count, comma-separated filenames
- `output/idf.txt` — `term<TAB>ln(N / df)`

`N` in the script is `$#files` after `readdir`. That is **not** automatically “number of `.txt` files.” See [known-quirks.md](known-quirks.md). The committed idf table behaves as if \(N = 18\).

### 2. `tf*idf-product.pl`

Loads `output/idf.txt` into a hash, then for each file in `output/tf/`:

```text
tfidf(term) = tf(term) * idf(term)
```

Writes `output/tfidf/<filename>` as `term<TAB>tfidf`, again alphabetically.

This script uses `Text::CSV_XS` with `sep_char => "\t"`. The tables are ordinary TSV; the helper scripts under `examples/` parse them with Python’s stdlib or with Perl’s built-in `split`.

## Output formats

All numeric tables are **tab-separated**, one term per line, **sorted by term** (string sort), not by score. That is why `sort -k2 -n` (or `examples/top_terms.py`) is the right way to find winners, and why a naive `sort -k2` on scientific notation can lie.

### `output/tf/<doc>`

```text
alice	0.0144867559678874
the	0.051234...
```

Second column is a fraction of tokens in that file. Values are in `[0, 1]`.

### `output/idf.txt`

```text
alice	1.79175946922805
macbeth	2.89037175789616
the	0
```

One global weight per term. `0` means “appears in every document.”

### `output/df.txt`

```text
word 	 #docs it exists in 	 doc names
alice	3	carroll-alice.txt, chesterton-thursday.txt, edgeworth-parents.txt
```

The filename list is the supporting evidence for the df integer. It is unordered (hash key order from the original Perl run).

### `output/tfidf/<doc>`

```text
alice	0.025956780390307
the	0
```

This is the table you actually rank.

## What you do *not* get

- No inverted index for querying “find documents about whales.”
- No cosine similarity between documents (you can build one from the tf-idf tables; `examples/compare_documents.py` lists shared vs distinctive high-scoring terms instead).
- No stemming, stopword file, or n-grams. `alice` and `alices` are different terms. `don't` becomes `dont`.
- No incremental update. Add a 19th book and you must rerun both scripts; every idf changes.

## Regenerating

```bash
mkdir -p output/tf output/tfidf
perl tf-idf-values.pl
perl 'tf*idf-product.pl'
```

Rerunning will overwrite `output/tf/`, `output/df.txt`, `output/idf.txt`, and `output/tfidf/`. The committed files are the reference snapshot this documentation quotes.

`output/df-sorted.txt` is a large extra dump (same information as `df.txt`, different order). The scripts do not recreate it.

## Helper path (no extra modules)

If you only want to *read* the committed tables:

```bash
python3 examples/top_terms.py output/tfidf/shakespeare-hamlet.txt --n 20
python3 examples/compare_documents.py \
    output/tfidf/carroll-alice.txt \
    output/tfidf/shakespeare-macbeth.txt
```

If you want a pipeline you can finish on paper, use the four-file corpus in `examples/toy-corpus/` and `examples/run_toy_example.py`. That runner mirrors the tokenization and the `tf * ln(N/df)` product, but it uses the true document count as \(N\).
