# Perl pipeline and file formats

Two scripts, three stages, four kinds of text table. Nothing here talks to a search engine; both programs read and write files under `gutenberg/` and `output/`.

```
gutenberg/*.txt
        │
        ▼
 tf-idf-values.pl
        │
        ├── output/tf/<book>.txt          one file per book
        ├── output/df.txt                 one row per distinct token
        └── output/idf.txt                one row per distinct token
                │
                ▼
     tf*idf-product.pl
                │
                └── output/tfidf/<book>.txt
```

## Stage 1 — `tf-idf-values.pl`

The script opens `gutenberg/`, skips names that begin with `.` (so `.` / `..` / `.DS_Store` are not tokenized), and for every remaining file:

1. Reads the whole file as lines.
2. Applies the four cleanup steps from the README.
3. Splits on spaces.
4. Counts tokens into `%tf` and records “this file contains this token” in `%df`.
5. Writes `output/tf/<filename>` as `token<TAB>tf` sorted by token.

After the last book it writes:

- `output/df.txt` — header line, then `token<TAB>df<TAB>file, file, …`
- `output/idf.txt` — `token<TAB>idf` with `idf = log($n / df)`

`$n` is `$#files`, the last index of the `readdir` array, **not** the number of books. That is the most important mismatch between the script and the committed tables; see [formula-and-implementation-notes.md](formula-and-implementation-notes.md).

The script is stdlib-only (`strict`, `opendir`, hashes). It does not create `output/tf/` or `output/tfidf/` for you; those directories already exist in the repo.

### `output/tf/<book>.txt`

```
1865	3.76279349789284e-05
a	0.0235927152317881
alice	0.0144867549668874
```

- One line per distinct token that survived cleanup.
- Second column is a Perl float (`count / $word_count`).
- Sort is alphabetical by token, not by score.
- Tokens that never occur in that book are omitted (sparse).

### `output/df.txt`

```
word 	 #docs it exists in 	 doc names
alice	3	chesterton-thursday.txt, carroll-alice.txt, edgeworth-parents.txt,
```

- First line is a header.
- `df` is the number of **files** in which the token occurred, not the total occurrence count.
- The file list is the hash-key order from Perl, so it is not alphabetical and not stable across Perl versions.
- There is a trailing comma and space after the last filename.

### `output/idf.txt`

```
alice	1.79175946922805
the	0
macbeth	2.89037175789616
```

No header. Same token order as the `df` loop (sorted keys). One published line is corrupt (`thatyou` with a trailing `y`); the notes file records it.

## Stage 2 — `tf*idf-product.pl`

This script does not retokenize the books. It:

1. Loads every `token → idf` pair from `output/idf.txt` using `Text::CSV_XS` with tab as the separator.
2. Walks `output/tf/`.
3. For each `token<TAB>tf` line, writes `token<TAB>(tf * idf)` to `output/tfidf/<same-name>`.

Missing `Text::CSV_XS` is a hard failure (`Can't locate Text/CSV_XS.pm`). The Python toy does the same multiply without that dependency.

### `output/tfidf/<book>.txt`

```
alice	0.0259567755003685
gryphon	0.00454723625187029
the	0
```

Same sparse, alphabetically sorted layout as the `tf` files. A zero here almost always means “this token’s IDF was 0”, i.e. it appeared in all 18 books.

## What the scripts do *not* do

- They do not rank. High-weight terms are not at the top of the file; `alice` happens to be near the top of Alice's table only because `a…` is early in the alphabet.
- They do not compute similarity. That step is described in the 2014 post and implemented here in `examples/python/similar_docs.py`.
- They do not skip stopwords, numbers, or one-character tokens. `1865` is a real row in Alice's table (the title line year).
- They do not stem. `whale` and `whales` are different rows.

To rank a committed table:

```bash
python3 examples/python/rank_terms.py --from-table output/tfidf/carroll-alice.txt --top 15
```

## Running order

```bash
# optional: start from a clean output tree
mkdir -p output/tf output/tfidf

perl tf-idf-values.pl
perl 'tf*idf-product.pl'
```

The second command must be quoted because of the `*` in the filename. A rerun **overwrites** `output/`; it does not merge.

If you only want to study the 2012 experiment, do not rerun. Use the committed files and the Python readers. If you want numbers you can defend against the formula \(N = 18\), use `examples/python/tfidf_toy.py` instead of the Perl `$#files` count.
