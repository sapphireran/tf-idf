# Pipeline: the two original Perl scripts

The blog-post calculation is two processes and a folder of intermediate
TSV files. Nothing is a web service. Nothing writes back into
`gutenberg/`.

```
gutenberg/*.txt
        │
        ▼
 tf-idf-values.pl
        │
        ├── output/tf/<file>     normalized TF per term per document
        ├── output/df.txt        document frequency + document names
        └── output/idf.txt       ln(N / df) per term
        │
        ▼
 tf*idf-product.pl
        │
        └── output/tfidf/<file>  TF * IDF per term per document
```

The teaching Python in `examples/python/` is a single program that
writes the same four artifacts for any input directory. Use that for
new examples. Treat the Perl as the historical snapshot.

## Pass 1: `tf-idf-values.pl`

### Inputs

- Every directory entry in `gutenberg/` whose name does **not** start
  with `.` (so `.DS_Store` is skipped, `bible-kjv.txt` is not).

### Per document

For each kept file the script:

1. Reads the whole file as lines.
2. Tokenizes each line with the rules in
   [tf-idf-explained.md](tf-idf-explained.md).
3. Increments `tf{term}` and records `df{term}{filename} = 1`.
4. Increments a running `word_count` for **every** field from
   `split(/ +/, ...)`, including empty fields. Empty fields are not
   added to `%tf`, so they dilute every TF share slightly. See
   [limitations.md](limitations.md).
5. Writes `output/tf/<filename>` as `term<TAB>tf`, terms sorted
   ascending.

### Collection

After every file has been read:

```
N        = $#files          # last index of readdir(), not a file count
idf(t)   = log(N / df(t))   # Perl log() is natural log
```

`readdir` includes `.` and `..`. That makes `$#files` easy to get wrong.
The **checked-in** `output/idf.txt` values match **`N = 18`**
(the number of `.txt` files), not `$#files` on a directory that also
contains `.`, `..`, and `.DS_Store`.

When you re-run the script on this checkout, recompute `N` from the
number of files you actually processed if you want to match `output/`.
The teaching Python does that: `N = number of non-hidden files`.

### Outputs

**`output/df.txt`**

```
word \t #docs it exists in \t doc names
alice	3	carroll-alice.txt, bryant-stories.txt, ...
```

Column 3 is a comma-separated list of filenames. The header row is
literal text, not a term.

**`output/idf.txt`**

```
alice	1.79175946922805
```

No header. Terms sorted ascending. Values are Perl default stringification
of a floating-point `log`.

## Pass 2: `tf*idf-product.pl`

### Inputs

- `output/idf.txt`
- every file in `output/tf/`

### Behavior

The script parses both TSV files with `Text::CSV_XS` (`sep_char => "\t"`).
For each term in a TF file:

```
tfidf(t, d) = tf(t, d) * idf(t)
```

Missing IDF keys become `0` in Perl (numeric context on `undef`). That
is another way a term can land at TF-IDF `0` besides a true `idf = 0`.

The product is written to `output/tfidf/<filename>` as `term<TAB>tfidf`,
terms sorted ascending. There is no ranking step in Perl. Rankings are
a later read, either by eye or with `examples/python/top_terms.py`.

### Dependency

`Text::CSV_XS` is a CPAN module. The teaching Python uses
`str.split("\t", 1)` instead so the examples run on a bare interpreter.

## Why two passes?

The split is the whole teaching value of the original project:

1. You can open `output/tf/carroll-alice.txt` and see that `alice` is a
   large share of the book and `a` is an even larger share.
2. You can open `output/idf.txt` and see that `a` has IDF `0` while
   `alice` does not.
3. You can open `output/tfidf/carroll-alice.txt` and see the product
   drop `a` to zero and keep `alice` at the top.

If the scripts only wrote TF-IDF, the "why is `the` gone?" question
would be harder to answer from the files alone.

## Re-running versus the snapshot

`output/` is a snapshot, not a cache that must stay live. Re-running
the Perl will overwrite it. Differences you should expect if you do:

| Cause | Effect |
| --- | --- |
| `.DS_Store` or extra files in `gutenberg/` | `readdir` changes; `$#files` changes; every IDF shifts |
| Perl version / `log` formatting | trailing digits in TSV may change |
| Locale or file encoding | unlikely for this ASCII-heavy corpus, but possible |
| Missing `output/tf/` or `output/tfidf/` directories | the scripts `open` with `>` and will fail if the parent dir is absent |

The teaching Python creates output directories and computes
`N = |processed files|`, so it is the safer way to regenerate numbers
for the toy corpora.

## Teaching Python equivalent

```bash
python3 examples/python/compute_tfidf.py \
  --input-dir gutenberg \
  --output-dir /tmp/gutenberg-tfidf
```

That writes `tf/`, `df.txt`, `idf.txt`, and `tfidf/` in the same TSV
shape. It will not bit-match `output/` (float formatting, document
order in `df.txt`, possible `word_count` differences). Rankings of the
distinctive names should still agree.

## Related

- TSV columns: [output-formats.md](output-formats.md)
- Quirks that change scores: [limitations.md](limitations.md)
