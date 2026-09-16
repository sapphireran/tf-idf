# The original Perl pipeline

Two scripts, two passes, four kinds of output. Both scripts were
written to be launched from the repository root. They assume `gutenberg/`
and `output/` already exist.

## Pass 1: `tf-idf-values.pl`

This is the heavier script. For every file in `gutenberg/` whose name
does not start with `.` it:

1. Reads the whole file as an array of lines.
2. Cleans each line:
   - `chomp`
   - collapse horizontal/vertical whitespace to a single space
   - `tr/[A-Z]/[a-z]/` (see the quirks doc; this happens to lowercase)
   - delete characters outside `[A-Za-z0-9]` and whitespace
3. Splits on spaces and skips empty tokens.
4. Counts tokens into `%tf` and records "term t was seen in file f"
   into `%df`.
5. Writes **normalized** TF to `output/tf/<filename>`:

   ```
   term<TAB>count/word_count
   ```

   Terms are sorted alphabetically, not by frequency.

After every file is processed it writes two corpus-level tables:

- `output/df.txt` — header row, then `term`, number of documents, then
  a comma-separated list of filenames.
- `output/idf.txt` — `term` and `log($n / df)`. Perl `log` is the
  natural logarithm.

`$n` is set with `my $n = $#files;` after `readdir`. That is **not**
the same as "number of `.txt` files." The committed `output/idf.txt`
values are nevertheless consistent with `N = 18` (the real document
count). Walk through the arithmetic in
[05-quirks-and-limitations.md](05-quirks-and-limitations.md).

`output/df-sorted.txt` is in the tree but is **not** produced by either
script. It is a sorted view of the DF table (useful, but extra).

## Pass 2: `tf*idf-product.pl`

The filename contains a glob character. Quote it in the shell:

```bash
perl 'tf*idf-product.pl'
```

The script:

1. Loads `output/idf.txt` into a hash, using `Text::CSV_XS` with
   `sep_char => "\t"`.
2. Reads every file in `output/tf/`.
3. For each term, writes `tf * idf` to `output/tfidf/<filename>`.
4. Again sorts alphabetically by term.

It does not print a ranking. A term with TF-IDF `0.025957` sits next to
whatever neighbors it has in dictionary order. That is why
`scripts/rank_precomputed_tfidf.py` exists.

If a TF line fails to parse, the script prints `Error: ...` and
continues. It never validates that every TF term has an IDF row; a
missing IDF would make the product `undef * number` and warn under
`use warnings` (which this file does not enable). The teaching Perl
clone turns warnings on.

## Directories the scripts expect

```
output/tf/      created by pass 1, one file per Gutenberg text
output/tfidf/   created by pass 2, same filenames
output/df.txt
output/idf.txt
```

Pass 1 opens `output/tf/$f` for write without `mkdir`. If you clone
this repo the folders are already there. A clean checkout that deleted
`output/tf` would need that directory recreated before a rerun.

## What the scripts do not do

- no command-line arguments (corpus path is hardcoded as `gutenberg`)
- no stopword file
- no stemming or lemmatization
- no length cutoff on tokens, so `o` and `1` are vocabulary
- no ranking / top-k printout
- no tests

`examples/tiny_tfidf.pl` and `examples/tfidf_toy.py` are the versions
meant to be read and rerun while following the worked examples.
