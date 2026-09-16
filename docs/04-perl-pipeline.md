# Perl pipeline

Two scripts produce the tables in `output/`. They are meant to be run from
the repository root, in order.

```bash
perl tf-idf-values.pl
perl 'tf*idf-product.pl'
```

The second filename must be quoted. The `*` is a literal character, not a
glob, but an unquoted shell will expand it.

Re-running the scripts overwrites the checked-in tables. The Python examples
read those tables; they do not need the Perl stack.

## Stage 1: `tf-idf-values.pl`

For every name in `gutenberg/` that does not start with `.`:

1. Read the file as raw lines.
2. `chomp`, squeeze horizontal/vertical whitespace, lowercase, strip every
   character outside `[a-zA-Z0-9]` and spaces.
3. Split on spaces. Empty strings are ignored; everything else increments
   a per-document counter and a collection-level `{term -> {filename}}` set.
4. Write `output/tf/<filename>` as `term<TAB>count/token_count`, sorted by
   term.

After the loop it writes two collection files:

* `output/df.txt` — header row, then `term`, `df`, and a comma-separated
  list of filenames that contain the term.
* `output/idf.txt` — `term<TAB>log(N / df)`.

Perl `log` is the natural logarithm. The IDF line is:

```perl
my $n = $#files;
my $idf_val = log($n / ($#vals + 1));
```

`$#vals + 1` is `df` (last index + 1). `$#files` is the last index of the
`readdir` array, which includes `.` and `..`. That is not the same as "how
many `.txt` files were processed." The checked-in `output/idf.txt` matches
`N = 18` (the processed texts), i.e. `ln(18 / df)`. If you regenerate with
the current script on a directory that also contains `.` / `..` /
`.DS_Store`, `$#files` will not be 18 and every IDF will shift.

The Python toy uses `N = number of processed documents` on purpose so it
agrees with the committed Gutenberg tables. Details and a safer Perl
snippet are in [07-tokenization-and-quirks.md](07-tokenization-and-quirks.md).

## Stage 2: `tf*idf-product.pl`

This script does not retokenize. It:

1. Loads `output/idf.txt` into a hash with `Text::CSV_XS` (tab-separated).
2. Walks every non-hidden file in `output/tf/`.
3. For each term, writes `TF * IDF` to `output/tfidf/<filename>`.

Missing `Text::CSV_XS` is a hard failure:

```
Can't locate Text/CSV_XS.pm in @INC
```

The files are ordinary `word<TAB>number` rows, so the Python readers parse
them with `str.split("\t")` and do not need the module.

A term that appears in a TF file but not in `idf.txt` would multiply by
`undef` and become `0` in Perl. That should not happen if both stages ran
on the same corpus.

## What is not in the pipeline

* No stopword list. IDF is the only filter.
* No stemming or case folding beyond `tr/[A-Z]/[a-z]/`.
* No sentence or chapter boundaries. A book is one bag of words.
* No query stage. Ranking and querying were added later as Python
  examples that consume `output/tfidf/`.

## Output that is not written by the scripts

`output/df-sorted.txt` is a checked-in companion of `df.txt` (same columns,
different row order). The Perl scripts do not rebuild it. Treat it as a
convenience snapshot.

`.DS_Store` files under `gutenberg/` and `output/` are Finder leftovers.
The scripts skip names that start with `.`; they should not appear as
documents in the TF-IDF tables. One did land in `output/tf/` as a binary
junk file from an earlier run — ignore it if you see it.

## Regenerating safely

If you only want to experiment, copy a couple of Gutenberg files into a
scratch directory and point a modified script at that path, or use
`examples/tiny_tfidf.py --corpus ...` which implements the same math
without touching `output/`.
