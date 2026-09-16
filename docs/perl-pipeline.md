# The original Perl pipeline

Two scripts, committed in 2012, produce the tables under `output/`.

```
gutenberg/*.txt
        │
        ▼
 tf-idf-values.pl
        │
        ├── output/tf/<file>     normalized term frequency
        ├── output/df.txt        term → document list
        └── output/idf.txt       term → log(N / df)
                │
                ▼
        tf*idf-product.pl
                │
                └── output/tfidf/<file>   tf * idf
```

They were written as a companion to a blog post
(`http://nlp-stuff.blogspot.com/2012/09/tfidf-example-and-implementation-details.html`).
That post is no longer available. This page reconstructs the behavior from
the scripts themselves.

## `tf-idf-values.pl`

The script opens `gutenberg/`, skips names that start with `.`, and for
each remaining file:

1. Reads the whole file into memory, line by line.
2. Cleans each line (see `docs/algorithm.md`).
3. Increments a per-file hash `%tf` and a global `%df{$term}{$filename}`.
4. Writes `output/tf/<filename>` as `term<TAB>count/word_count`.

After every file is read it writes `df.txt` and `idf.txt`.

### Document count

```perl
my $n = $#files;
my $idf_val = log($n/($#vals+1));
```

`$#files` is the last index of the `readdir` array, not the number of
processed documents. `readdir` includes `.` and `..`, and this checkout
also has `gutenberg/.DS_Store`.

The committed `output/idf.txt` has a maximum of `2.89037175789616`, which
is `log(18)` to machine precision. So the tables that shipped with the
repo were produced with **N = 18**, the number of `.txt` files. Re-running
the script today against this directory listing will not reproduce that
`N` unless you change the counting.

The Python CLI counts processed documents:

```python
n_documents = len(list_of_kept_files)
idf = log(n_documents / df)
```

That is the number the original tables actually used.

### `$word_count` and empty split fields

Inside the token loop the Perl increments `$word_count` *before* it
rejects the empty string. Combined with `split(/ +/, ...)`, a cleaned line
that starts with a space contributes an empty field to the denominator
but not to `%tf`. Indented Gutenberg lines therefore make TF slightly
smaller than `count / non_empty_tokens`.

The effect is small on novels and large on pathological input. The
Python default ignores empty fields. Pass `--perl-compat` to keep them.

### `df.txt` formatting

Each row looks like:

```
whale	2	melville-moby_dick.txt, some-other.txt,
```

The trailing comma is in the original print loop. The Python writer keeps
that shape so a visual diff against `output/df.txt` stays readable.

## `tf*idf-product.pl`

This script is only a join:

1. Read `output/idf.txt` into a hash (via `Text::CSV_XS` with tab as the
   separator).
2. For each file in `output/tf/`, multiply each TF by the stored IDF.
3. Write `output/tfidf/<file>`.

It depends on `Text::CSV_XS`. The compute script does not. If you want to
re-run the 2012 path on a machine without that module, use the Python
CLI instead:

```bash
python3 -m tfidf compute gutenberg -o /tmp/gutenberg-tfidf
```

That command will take a while on `bible-kjv.txt` and
`melville-moby_dick.txt`. It is not required for the unit tests; those
use `examples/`.

## What the committed `output/` is

`output/` is a snapshot, not a cache that the Python package reads by
default. Commands:

| goal | command |
| --- | --- |
| inspect the 2012 snapshot | `python3 -m tfidf top-tsv output/tfidf --n 10` |
| recompute on Gutenberg | `python3 -m tfidf compute gutenberg -o /tmp/out` |
| recompute on a tiny example | `python3 -m tfidf report examples/tiny-corpus` |

`output/df-sorted.txt` is a one-line leftover from the original dump and
is not used by either script.

## File names that start with a dot

Both Perl scripts skip `^\..*` and then process every remaining name.
That is why `.DS_Store` is not a document and why a stray `.bak` would
be treated as one. The Python helper `iter_corpus_files` skips hidden
names too, and additionally defaults to `*.txt` so a README sitting
next to an example corpus is not scored.
