# Pipeline: from `gutenberg/` to `output/tfidf/`

Two Perl scripts implement the formulas in [`tf-idf-explained.md`](tf-idf-explained.md).
They were written as a 2012 toy; paths are hard-coded and there is no CLI.

```
gutenberg/*.txt
        │
        ▼
 tf-idf-values.pl
        │
        ├── output/tf/<file>.txt     term<TAB>tf
        ├── output/df.txt            term<TAB>df<TAB>filenames
        └── output/idf.txt           term<TAB>idf
                │
                ▼
        tf*idf-product.pl
                │
                └── output/tfidf/<file>.txt   term<TAB>tf*idf
```

## Script 1: `tf-idf-values.pl`

**Reads:** every directory entry in `gutenberg/` whose name does not start with `.`.

**Writes:**

- `output/tf/<filename>` — sorted alphabetically by term
- `output/df.txt` — header line, then one row per term
- `output/idf.txt` — no header, one row per term

**Per file** it:

1. Reads the entire file into a list of lines.
2. Tokenizes each line (lowercase, strip non-alphanumerics, split on spaces).
3. Increments a per-file `%tf` hash and a global `%df` hash-of-hashes
   (`$df{$term}{$filename} = 1`) so each file counts at most once per term.
4. After the file is consumed, writes `term<TAB>(count / $word_count)`.

**After all files** it:

1. Sets `$n = $#files` (last index of the raw `readdir` array, **not** the
   filtered `.txt` count). See the `N` note below.
2. For each term, `df = number of keys in $df{$term}`.
3. Writes `idf = log($n / $df)` using Perl's natural log.

The script prints `Processing file: <name>` on STDERR/stdout as it goes. It will
also attempt to process `gutenberg/.DS_Store` because that name does not start
with `.`. The checked-in TF/IDF tables do not include a `.DS_Store` document,
so they come from a run that either lacked that file or skipped it some other
way.

### The `N` used for IDF

Perl's `$#files` is `scalar(@files) - 1`. `readdir` includes `.` and `..`, so a
directory with 18 texts yields `N` close to, but not necessarily equal to, 18.

The **checked-in** `output/idf.txt` matches `N = 18` exactly:

```
ln(18) = 2.8903717578961645
```

Every singleton term in that file (`macbeth`, `harriet`, `buster`, …) has IDF
`2.89037175789616`. A fresh run of the current script on this directory listing
may not reproduce that constant. If you need bit-identical IDF, set `N` to the
number of documents you actually scored (here, 18 text files).

The 2012 commit `b50ebb9` (“correcting idf values in calculating number of
files”) is the historical fix for this off-by-one; the remaining `$#files`
quirk is documented rather than rewritten, so the original scripts stay
intact.

## Script 2: `tf*idf-product.pl`

**Reads:** `output/idf.txt` and every non-dot file in `output/tf/`.

**Writes:** `output/tfidf/<filename>` with `term<TAB>(tf * idf)`.

It parses TSV lines with `Text::CSV_XS` (`sep_char => "\t"`). That module is
**not** in Perl core:

```bash
cpanm Text::CSV_XS
# Debian/Ubuntu: sudo apt-get install libtext-csv-xs-perl
```

If a TF line fails to parse, the script prints `Error: <input>` and skips the
row. The output file handle is not explicitly closed; Perl closes it when the
handle is reused or the process exits.

Terms are written in alphabetical order (`sort keys %tfidf`), not by score.
Use [`../examples/rank_top_terms.py`](../examples/rank_top_terms.py) or
`sort -t$'\t' -k2,2nr` to rank them. Scientific notation in the TSV is numeric;
a **string** sort on column 2 will put `9.96e-05` above `0.010` and give a
nonsense “top terms” list.

## What the scripts do not do

- No stemming, stop-word list, or case folding beyond `tr/[A-Z]/[a-z]/`.
- No sentence or paragraph boundaries. Newlines are just more whitespace.
- No command-line corpus path, encoding flag, or output directory.
- No incremental update: rerunning overwrites `output/`.
- No query-time API. This is a batch scorer, not a search engine.

## Re-running vs. trusting `output/`

For reading examples, **trust the checked-in `output/`**. Those files are the
2012 result set the rest of the docs quote.

Re-run only if you are changing tokenization or want to confirm the scripts
still execute. The tiny corpus in `examples/tiny-corpus/` is the better place
to experiment: it finishes instantly and has a verifier.

## Python counterpart

[`../examples/tiny-corpus/compute_tfidf.py`](../examples/tiny-corpus/compute_tfidf.py)
implements the same formulas with an explicit `--corpus` / `--output` and with
`N = number of scored documents`. Use that script for new personal experiments.
Leave the Perl pair as the historical implementation.
