# Perl pipeline

Two scripts turn the files in `gutenberg/` into the tables in `output/`.
They were written as a blog-post toy in 2012 and are intentionally
small. This page is a line-by-line reading, not a rewrite.

```
gutenberg/*.txt
        │
        ▼
 tf-idf-values.pl
        │
        ├── output/tf/<same-filename>     word → TF
        ├── output/df.txt                 word → df + document list
        └── output/idf.txt                word → IDF
                │
                ▼
        tf*idf-product.pl
                │
                └── output/tfidf/<same-filename>   word → TF × IDF
```

Run them from the repository root, with `output/tf` and `output/tfidf`
already present:

```bash
perl tf-idf-values.pl
perl 'tf*idf-product.pl'
```

The second script needs the CPAN module `Text::CSV_XS` (used only as a
tab splitter). The first script is core Perl.

## `tf-idf-values.pl`

### Directory scan

```perl
opendir(DIR,"gutenberg");
my @files = readdir(DIR);
```

Every directory entry is collected, including `.`, `..`, and any
`.DS_Store`. The later `if ($f !~ /^\./)` guard skips those names when
**processing** a file, but it does not rebuild `@files`. That matters
for \(N\); see [quirks-and-variants.md](quirks-and-variants.md).

### Per-document TF

For each kept file the script:

1. Reads the whole file into an array of lines.
2. Tokenizes each line (below).
3. Increments `$tf{$d}` and `$word_count` for every non-empty token.
4. Also records `$df{$d}{$f} = 1` so document frequency is a set of
   filenames, not a raw count of occurrences.
5. Writes `output/tf/$f` with `tf = count / $word_count`.

`$word_count` is incremented **before** the empty-token check. A line
that tokenizes to nothing still does not add empty keys, but a run of
spaces does not inflate the denominator either, because `split(/ +/)`
does not produce empty fields between consecutive spaces. A token that
fails `if ($d ne "")` is rare; the increment-before-check is harmless
for the Gutenberg files.

### Tokenization

Per line, in order:

| Step | Code | Effect |
| --- | --- | --- |
| 1 | `chomp` | Drop the newline. |
| 2 | `s/[\h\v]+/ /g` | Collapse horizontal/vertical whitespace to a single space. |
| 3 | `tr/[A-Z]/[a-z]/` | Lowercase. The character-class brackets are unnecessary in `tr///` but do not change the result for ASCII. |
| 4 | `s/[^a-zA-Z\d\s]//g` | Delete punctuation and any remaining non-alphanumeric, non-space character. Apostrophes disappear: `Alice's` → `alices`, `don't` → `dont`. |
| 5 | `split(/ +/, $txt)` | Split on one or more spaces. |

There is no stopword list, no stemming, no sentence splitter, and no
special handling of Project Gutenberg headers or license footers.

Hyphenated words become glued (`white-rabbit` is not in these files, but
`ebook` style compounds and speech prefixes survive only if they were
already alphanumeric). Shakespeare speaker tags such as `Ham.` become
`ham` after the period is stripped — which is why `ham` outranks
`hamlet` in `output/tfidf/shakespeare-hamlet.txt`.

### Document frequency dump

`output/df.txt` starts with a header line

```
word 	 #docs it exists in 	 doc names
```

then one row per vocabulary item:

```
term<TAB>df<TAB>file1.txt, file2.txt, ...
```

The filename list is the hash-key order of `%{ $df{$t} }`, so it is not
alphabetical and is not stable across Perl versions. `output/df-sorted.txt`
is a separately sorted convenience copy; the scripts do not regenerate
it.

### IDF dump

```perl
my $n = $#files;
...
my $idf_val = log($n/($#vals+1));
```

`$#files` is the last index of `@files`, i.e. `scalar(@files) - 1`.
`$#vals + 1` is the true document frequency. Combined with `.` / `..` /
`.DS_Store`, a fresh run of the script as committed does **not**
reproduce `output/idf.txt`, which uses \(N = 18\). The 2012 bugfix
rewrote the output tables to \(N = 18\) without changing this line.

The companion scripts in `examples/` take an explicit `--n-docs` (default:
count of readable documents) so the math stays inspectable.

## `tf*idf-product.pl`

The product script:

1. Loads `output/idf.txt` into a hash, using `Text::CSV_XS` with
   `sep_char => "\t"`.
2. For each file in `output/tf/`, reads `word<TAB>tf` and writes
   `word<TAB>tf*idf` under `output/tfidf/`.
3. Sorts keys alphabetically, same as the TF files.

It does not re-tokenize and does not recompute IDF. If you edit a TF
file by hand and rerun only the product script, IDF stays stale.

Missing IDF keys become `undef`, which Perl numifies to `0` in the
multiplication. That silently zeros unknown terms.

The `else` branch prints a CSV parse error and continues. A trailing
blank line in a TF file would trigger it.

## File formats

All generated tables are UTF-8-or-ASCII TSV with no quoting.

| File | Columns | Sorted by |
| --- | --- | --- |
| `output/tf/<doc>` | term, TF | term |
| `output/idf.txt` | term, IDF | term |
| `output/df.txt` | term, df, filenames | term (header on row 1) |
| `output/tfidf/<doc>` | term, TF × IDF | term |

There is no `output/tfidf` header row. Rank by the second column
yourself; `examples/rank_terms.py` does that.

## What a rerun overwrites

Both scripts truncate their output files. They do not delete leftover
names if you remove a book from `gutenberg/`. They also have no
`--outdir` flag. Treat `output/` as a cached experiment, not as an
append-only log.

The checked-in `output/` tree is the 2012 Gutenberg run after the
\(N = 18\) IDF correction. Keep it unless you intentionally want to
regenerate ~50k vocabulary rows.
