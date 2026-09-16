# How the Perl pipeline is wired

There are two scripts and four output families. Nothing is compiled.
You run the first script to get TF, DF, and IDF, then the second
script to multiply TF by IDF.

```
gutenberg/*.txt
        │
        ▼
 tf-idf-values.pl
        │
        ├── output/tf/<book>.txt      term → count / |d|
        ├── output/df.txt             term → df, file list
        └── output/idf.txt            term → ln(N / df)
                │
                ▼
        tf*idf-product.pl
                │
                └── output/tfidf/<book>.txt   term → tf * idf
```

## `tf-idf-values.pl`

The script opens `gutenberg/`, skips names that start with `.`, and
for every remaining file:

1. Reads all lines into memory.
2. Tokenizes each line as described in
   [tokenization](02-tokenization.md).
3. Counts tokens in a `%tf` hash and records document membership in a
   `%df` hash-of-hashes (`$df{$term}{$filename} = 1`).
4. Writes a normalized TF file under `output/tf/`.

After every file has been read, it walks the keys of `%df`, writes the
human-readable DF table, and writes `output/idf.txt` with
`log($n / df)`.

The membership trick is the whole DF implementation: a term seen in
the same file a thousand times still has one key in
`$df{$term}`, so `keys %{ $df{$term} }` is the document frequency.

## `tf*idf-product.pl`

This script does not reread the books. It:

1. Loads every `term → idf` row from `output/idf.txt` using
   `Text::CSV_XS` with a tab separator.
2. Opens each file in `output/tf/`.
3. Multiplies `tf * idf` for each term.
4. Writes `output/tfidf/<same filename>`.

It is a join on term strings. If you edit tokenization in the first
script and forget to rerun the second, the product files go stale.

## Why the outputs are committed

The Gutenberg sample is large enough that rerunning the Perl path is
slow and requires `Text::CSV_XS`. The committed `output/` directory is
the original toy result from the 2012 example, including the IDF
bugfix in `b50ebb9` that recomputed the collection size.

You do not need to regenerate those files to study them. Use:

```bash
python3 examples/python/inspect_gutenberg.py --only carroll-alice.txt melville-moby_dick.txt
```

## What the Python path adds

`examples/python/tfidf_lab.py` is a second implementation of the same
formulas, written so a five-document corpus can be scored, compared,
and tested without Perl modules. It is not a rewrite of the Gutenberg
job and it does not replace the committed tables.

Use the Python path when you want to:

- change a document and see new top terms in a second
- print every cell of the three-sentence classroom example
- compare two books with cosine similarity
- generate the HTML report in `examples/tiny_corpus/expected/report.html`
