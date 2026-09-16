# Original Perl pipeline

The 2012 walkthrough is two scripts plus committed result files.

```
gutenberg/*.txt
        │
        ▼
 tf-idf-values.pl
        │
        ├── output/tf/<file>     term<TAB>normalized_tf
        ├── output/df.txt        term<TAB>df<TAB>file, file, ...
        └── output/idf.txt       term<TAB>ln(N / df)
                │
                ▼
     'tf*idf-product.pl'
                │
                └── output/tfidf/<file>   term<TAB>tf * idf
```

Neither script takes command-line paths. They assume you run them from
the repository root. The product script's filename contains a `*`; quote
it (`perl 'tf*idf-product.pl'`) or the shell expands it.

The cleaned rewrite that *does* take `--input` / `--output` is
[`examples/perl/compute_tf_idf.pl`](../examples/perl/compute_tf_idf.pl).

## `tf-idf-values.pl`

### File loop

`readdir` on `gutenberg/` yields `.`, `..`, any `.DS_Store`, and the 18
texts. The script skips names that match `/^\./`, so hidden files are
not tokenized. It still keeps the full `readdir` list around for `N`
(see below).

### Tokenization, line by line

For each non-hidden file the script:

1. Reads the whole file into an array of lines.
2. `chomp`s the newline.
3. Collapses horizontal and vertical whitespace to a single space
   (`s/[\h\v]+/ /g`).
4. Lowercases with `tr/[A-Z]/[a-z]/` (the brackets in the
   transliteration sets map to themselves).
5. Deletes every character that is not alphanumeric or whitespace
   (`s/[^a-zA-Z\d\s]//g`). Apostrophes disappear: `Alice's` → `alices`,
   `don't` → `dont`.
6. Splits on one or more spaces.

Empty tokens are not stored in `%tf` or `%df`, but the loop still does
`$word_count++` *before* the empty check. A leading space on a line
therefore inflates the tf denominator. After the whitespace collapse,
that happens on lines that started with indent. The Python example
defaults to the cleaner rule (empty tokens do not count); pass
`--faithful-perl` if you want the denominator quirk.

### Term frequency

```
tf(t, d) = count(t, d) / word_count(d)
```

Written to `output/tf/<filename>` as `term<TAB>value`, sorted by term.

### Document frequency

`%df` is a two-level hash: `$df{$term}{$filename} = 1`. That is a set of
documents per term. The printed `df` is `keys %{$df{$term}}`.

`output/df.txt` starts with a header line, then
`term<TAB>df<TAB>file, file, ...`. `output/df-sorted.txt` is a
hand-sorted sibling from the original dump; the script does not write
it.

### Inverse document frequency

```perl
my $n = $#files;
my $idf_val = log($n / ($#vals + 1));
```

Perl's `log` is the natural logarithm. `$#vals + 1` is `df`. `$#files`
is the **last index** of the `readdir` array, not `scalar(@files)` and
not the number of texts that were actually processed.

| If `gutenberg/` contains | `scalar @files` | `$#files` | processed texts |
| --- | --- | --- | --- |
| 18 `.txt` + `.` + `..` | 20 | 19 | 18 |
| 18 `.txt` + `.` + `..` + `.DS_Store` | 21 | 20 | 18 |

The committed `output/idf.txt` has a ceiling of `2.89037175789616`,
which is `ln(18)`. So the files that were scored in 2012 used `N = 18`,
i.e. the true document count. Re-running the script today with a
`.DS_Store` in `gutenberg/` would use a different `N` and rewrite every
idf. That is the main reason the example implementations count
processed documents instead of `$#files`.

`log(N / N) = 0` for terms that appear in every document. Those zeros
are visible in `output/idf.txt` for `the`, `and`, `a`.

## `tf*idf-product.pl`

The product script:

1. Loads `output/idf.txt` into a hash with `Text::CSV_XS` (`sep_char`
   is tab).
2. Reads each `output/tf/<file>`.
3. Writes `term<TAB>(tf * idf)` to `output/tfidf/<file>`.

It does not re-tokenize and it does not recompute `N`. If `idf.txt` and
the `tf/` files disagree about the vocabulary, missing idf lookups
become empty-string multiplication (Perl numifies that to 0).

The `else` branch prints `Error: …` when a line fails CSV parse.
Tab-separated `term<TAB>float` lines from the first script should not
hit that path.

## What the committed `output/` is

A snapshot of one successful 2012 run, not something the repo
regenerates in CI. Treat it as fixture data:

- `output/tf/` — 18 per-document tf tables (plus a copied `.DS_Store`)
- `output/idf.txt` — 57,368 terms
- `output/df.txt` — same vocabulary plus posting lists
- `output/tfidf/` — the products

[`examples/python/top_terms.py`](../examples/python/top_terms.py) ranks
those tables without running Perl.

## Bugfix commit

`b50ebb9` (“correcting idf values in calculating number of files”)
introduced `$n = $#files`. The original version used a different `N`
(likely `scalar @files`, which includes `.` and `..`). The cleaned
scripts just count the files they tokenize.
