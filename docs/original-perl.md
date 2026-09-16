# The 2012 Perl scripts

Two files do all of the original work. They are personal toy code
from 2012, left in the shape they were checked in. This page is a
reading guide so you do not have to reverse-engineer them from the
line noise.

Run both from the repository root. Paths are hard-coded to
`gutenberg/` and `output/`.

```bash
perl tf-idf-values.pl          # TF per file, plus DF and IDF
perl 'tf*idf-product.pl'       # TF * IDF per file
```

The filename `tf*idf-product.pl` has a literal `*` in it. Quote it
in the shell or the glob will expand.

## `tf-idf-values.pl` — counts and IDF

This is the only script that reads the books.

### Directory walk

```perl
opendir(DIR,"gutenberg");
my @files = readdir(DIR);
```

`@files` is every directory entry, including `.`, `..`, and
`.DS_Store`. A later check, `if ($f !~ /^\./)`, skips names that
start with a dot, so only the 18 `.txt` files are tokenized. The
skip does **not** shrink `@files` itself. That matters for `$n`
below.

### Per-file TF

For each kept file the script:

1. Reads every line into `@text`.
2. Runs the tokenizer described in [`algorithm.md`](algorithm.md).
3. Tallies `%tf` (term → raw count) and a running `$word_count`.
4. Writes `output/tf/<filename>` as `term<TAB>count/word_count`.

`%tf` is lexically inside the file loop, so it resets each book.
`%df` is declared outside the loop and accumulates across books.

Document frequency is stored as a hash-of-hashes:

```perl
$df{$d}{$f} = 1;
```

The inner key is the filename. Using `1` as the value makes the
structure a set: a hundred hits in one book still occupy one inner
key. `keys %{ $df{$t} }` is therefore `df(t)`.

### Global DF and IDF

After every file has been read:

```perl
my $n = $#files;
my $idf_val = log($n / ($#vals + 1));
```

`$#vals + 1` is the usual Perl "length of this array" idiom and is
the correct `df`. `$#files` is **not** the document count. It is
the last index of the unfiltered `readdir` list.

On this checkout `gutenberg/` has 21 entries (18 texts + `.` +
`..` + `.DS_Store`), so `$#files == 20`. A live run would write
`ln(20 / df)`. The tables already in `output/idf.txt` were produced
with `N = 18`. Commit `b50ebb9` ("Bugfix: correcting idf values in
calculating number of files") is what landed `$n = $#files`; the
checked-in numbers look like an earlier or side-door run that used
the real document count.

Practical rule:

- Want to **match `output/`**? Use `N = 18` (the benchmark default).
- Want to **match a fresh `perl tf-idf-values.pl`**? Use
  `--n-mode perl-last-index`.

`output/df.txt` starts with a header line and lists the filenames
that contain each term. `output/idf.txt` has no header, just
`term<TAB>idf`. `output/df-sorted.txt` is a derived listing that
these scripts do not regenerate; treat it as a leftover snapshot.

One gold cell is corrupt: `thatyou` is stored as `2.89037175789616y`
instead of `2.89037175789616` (`ln(18)`). The rest of that line is
an ordinary singleton-term IDF. The benchmark strips the trailing
letter when it loads `output/idf.txt` rather than failing the
whole comparison over a 2012 typo.

### What the script does not do

- It never writes TF-IDF. That is the second script.
- It never ranks terms.
- It never skips stop words.
- It never opens a file with an encoding layer. On this English
  ASCII/Latin-1 sample that is harmless.

It also has no `use warnings` and no checks that `output/tf/`
exists. A clean tree without those directories will fail at
`open(OUT,">output/tf/$f")`.

## `tf*idf-product.pl` — the multiply

This script never looks at `gutenberg/`. It only joins two tables
the first script already wrote.

### Reading IDF

```perl
use Text::CSV_XS;
my $csv = Text::CSV_XS->new({sep_char => "\t"});
```

Each line of `output/idf.txt` is parsed as a one-row TSV. Column 0
is the term, column 1 is the IDF. The result is `%idf`.

`Text::CSV_XS` is a CPAN module, not core Perl. If it is missing
you will get `Can't locate Text/CSV_XS.pm`. The personal Python
benchmark does not need it.

### Reading TF and writing TF-IDF

For each file in `output/tf/` (again skipping `^\.`):

```perl
my $val = $cols[1] * $idf{$cols[0]};
```

Missing IDF keys would multiply as `undef` and warn under
`use warnings`; in this pipeline every TF term was also counted
toward DF, so the key is always present.

The output file is `output/tfidf/<same filename>`, terms sorted
by name, same TSV shape as the TF files.

On a parse error the script prints `Error: ...` and continues.
It never deletes a stale output file, so a term that disappeared
from TF after a tokenizer change can linger until you wipe
`output/tfidf/` yourself.

## End-to-end data flow

```
gutenberg/*.txt
        │
        ▼
 tf-idf-values.pl
        │
        ├── output/tf/<book>.txt     term → count / word_count
        ├── output/df.txt            term → df, filenames
        └── output/idf.txt           term → ln(N / df)
                │
                ▼
        tf*idf-product.pl
                │
                └── output/tfidf/<book>.txt   term → tf * idf
```

Two passes on disk were a 2012 convenience: you can inspect TF
without recomputing IDF, and you can re-multiply if you edit an
IDF cell by hand. They are not required. The Python benchmark
keeps everything in memory and writes nothing unless you pass
`--write-report`.

## Reproducing, versus shadowing

"Reproduce `output/`" and "rerun the Perl" are different targets
on this tree.

| Goal | What to run | Expected `N` |
| --- | --- | --- |
| Confirm the checked-in tables | `python3 scripts/tfidf_benchmark.py --compare-output` | 18 |
| Shadow today's Perl | `perl tf-idf-values.pl` then the product script | `$#files` |
| Isolated arithmetic check | `python3 scripts/tfidf_benchmark.py --self-test` | 3 |

If you rerun the Perl, `git diff output/` will light up almost
every IDF line because `N` changed. That is not a corpus change;
it is the `$#files` line.

## Historical crumbs

- `a170430` — first check-in: scripts, `gutenberg/`, `output/`.
- `b50ebb9` — IDF `N` set to `$#files`.
- `cbdd56f` — one-line README pointing at the blog post.

The blog URL in that first commit is a 404 now. The scripts and
the tables are the remaining artifact. I am documenting them in
place rather than "fixing" the Perl: a silent change to `$n`
would make a new run disagree with every number already in
`output/`, which is worse than leaving a commented quirk.

If you do want a Perl-side fix later, the honest one is:

```perl
my @docs = grep { $_ !~ /^\./ } @files;
my $n = scalar @docs;
```

and a deliberate regeneration of `output/`. Until then the
benchmark is the place that states `N` out loud.
