# Pipeline

Two Perl programs, run from the repository root, produce every file under `output/`.

```
gutenberg/*.txt
        │
        ▼
 tf-idf-values.pl
        │
        ├── output/tf/<book>.txt     length-normalized TF, one file per book
        ├── output/df.txt            document frequency + book names
        └── output/idf.txt           ln(N / df)
                │
                ▼
        tf*idf-product.pl
                │
                └── output/tfidf/<book>.txt
```

You do not need to rerun this to read the notes. The committed `output/` tree is a completed run over the 18 texts.

## Script 1: `tf-idf-values.pl`

Responsibilities:

1. `opendir` on `gutenberg/`.
2. Skip names that begin with `.` (so `.`, `..`, and `.DS_Store` are not treated as books).
3. For each remaining file:
   - tokenize every line ([tokenization.md](tokenization.md))
   - accumulate `tf` counts in a per-file hash
   - mark `df{term}{filename} = 1`
   - write `output/tf/<filename>` as `term<TAB>tf` for every term, sorted by term
4. After all files:
   - write `output/df.txt` with a header line and one row per term
   - write `output/idf.txt` as `term<TAB>idf` with no header

The TF write happens **inside** the file loop, so you can watch `output/tf/` fill while the script is still reading later books. DF and IDF are collection statistics and only make sense after the last file.

### How N is chosen

The IDF line is:

```perl
my $n = $#files;
my $idf_val = log($n / ($#vals + 1));
```

`@files` is the raw `readdir` list, **including** `.` and `..` (and `.DS_Store` when present). `$#files` is the last index, not `scalar @files` and not the number of books actually processed.

The committed `output/idf.txt` uses `ln(18 / df)`, i.e. one document per `.txt`. That is the number the rest of these notes treat as `N`. If you rerun the script in an environment where `readdir` returns extra dotfiles, hapax IDF will no longer be `2.89037175789616`.

[known-quirks.md](known-quirks.md) records this in more detail. The Python example takes `--n` defaulting to the count of non-hidden `*.txt` files, which matches the committed tables.

### Directories the script expects

`tf-idf-values.pl` opens `output/tf/$f` for write. It does not `mkdir`. The `output/tf/` and `output/tfidf/` directories are already in the repo. A clean checkout can rerun the script; a fresh clone that deleted `output/` needs those folders created first:

```bash
mkdir -p output/tf output/tfidf
perl tf-idf-values.pl
```

## Script 2: `tf*idf-product.pl`

The filename contains a literal asterisk. Always quote it:

```bash
perl 'tf*idf-product.pl'
```

Responsibilities:

1. Parse `output/idf.txt` with `Text::CSV_XS` configured as tab-separated.
2. `readdir` on `output/tf/`.
3. For each non-dot file, multiply each TF by the IDF of the same term.
4. Write `output/tfidf/<filename>` as `term<TAB>tfidf`, sorted by term.

Missing IDF keys become implicit `0` in Perl (`undef` times a number is `0` with a warning if you turn warnings on — this script uses `use strict` only). After a consistent run of script 1, every TF term has an IDF row.

### Text::CSV_XS

The module is used as a TSV parser, not as a comma CSV writer. It protects against fields that might contain tabs (they do not, in this corpus). Install from CPAN if the script dies on `use Text::CSV_XS`.

The Python example does not need that module; it splits on the first tab.

## What is *not* in the pipeline

- No sort-by-score step. `output/tfidf/*.txt` is alphabetical, which is why `extract_top_terms.py` exists.
- No `output/df-sorted.txt` writer in the current scripts. That file is present in the tree (and is enormous) but is not produced by the two programs above. Treat it as a leftover artifact.
- No incremental update. Changing one Gutenberg file means rerunning both scripts for the whole collection, because IDF depends on every document.

## End-to-end commands

From the repository root:

```bash
mkdir -p output/tf output/tfidf
perl tf-idf-values.pl
perl 'tf*idf-product.pl'
python3 examples/python/extract_top_terms.py output/tfidf/melville-moby_dick.txt
```

For the toy collection only:

```bash
python3 examples/python/tfidf_example.py \
  --input-dir examples/tiny-corpus/docs \
  --output-dir /tmp/tiny-tfidf
diff -u examples/tiny-corpus/expected/idf.txt /tmp/tiny-tfidf/idf.txt
```

## Memory and time

The Gutenberg pass holds, for each book, a hash of that book's vocabulary, and globally a hash of term → set of filenames. *Moby-Dick* plus the KJV plus Whitman produce on the order of 57k distinct terms. That easily fits in memory on any machine that can hold the texts.

The expensive part is printing 18 alphabetical TF files and one 57k-row DF file. Rerunning from a laptop is fine; there is no need for a database.

## Failure modes worth knowing

| symptom | likely cause |
| --- | --- |
| `Can't locate Text/CSV_XS.pm` | script 2 dependency missing |
| empty `output/tfidf/` after script 2 | script 1 never ran, or `output/idf.txt` is empty |
| IDF hapax is `2.9957` or `3.0445` instead of `2.8904` | `N` picked up extra `readdir` entries |
| `alice` TF-IDF is 0 | Alice was copied into a second file, so `df` rose and, if it reached `N`, IDF became 0 |
| permission error on `output/tf/...` | `output/tf` directory missing |

Those cases are all local to this personal experiment; they are not general IR failures.
