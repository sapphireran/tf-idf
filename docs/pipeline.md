# Perl pipeline

Two scripts, two stages. Nothing is a daemon and nothing talks to a network. You run them from the repository root so the relative paths `gutenberg/` and `output/` resolve.

```text
gutenberg/*.txt
        │
        ▼
tf-idf-values.pl ──► output/tf/<file>
                   ──► output/df.txt
                   ──► output/idf.txt
        │
        ▼
tf*idf-product.pl ──► output/tfidf/<file>
```

Create the output directories if you have a clean checkout:

```bash
mkdir -p output/tf output/tfidf
```

`tf*idf-product.pl` has a `*` in the filename. Quote it in the shell: `perl 'tf*idf-product.pl'`.

## Stage 1: `tf-idf-values.pl`

The script is a single pass over `gutenberg/` plus a final write of the corpus tables. It uses `strict` and no modules.

### Directory listing

```perl
opendir(DIR,"gutenberg");
my @files = readdir(DIR);
```

`readdir` returns `.`, `..`, and every filename. The per-file loop skips names that match `/^\./`. The later assignment `$n = $#files` does **not** skip them. That is the \(N\) quirk discussed below.

### Per-file tokenization

For each real file the script:

1. Reads the whole file into `@text`.
2. `chomp`s each line.
3. Collapses Unicode horizontal/vertical whitespace with `$txt =~ s/[\h\v]+/ /g`.
4. Lowercases with `tr/[A-Z]/[a-z]/`.
5. Deletes non-alphanumerics with `$txt =~ s/[^a-zA-Z\d\s]//g`.
6. `split(/ +/, $txt)` and walks tokens.

Two counters move together:

- `$word_count++` for **every** split field, including empty strings.
- `$tf{$d}++` and `$df{$d}{$f}=1` only when `$d ne ""`.

Empty fields appear when a line has leading spaces or becomes blank after punctuation stripping. They inflate `$word_count` by a few tokens on messy lines and therefore shrink every normalized tf in that file by a tiny amount. The tiny-corpus Python helper omits empties from the denominator on purpose and documents the difference.

`%df` is a two-level hash: term → filename → `1`. Using the filename as a key is what makes df a **set** (presence), not a raw count.

### Per-file tf output

```perl
open(OUT,">output/tf/$f");
foreach my $t (sort keys %tf)
{
    print OUT $t."\t".($tf{$t}/$word_count)."\n";
}
```

One line per term, tab-separated, **sorted by term** (ASCII), not by score. Values are raw Perl floats (`0.0235927152317881` style). Re-running on a different Perl build can change the last digits; the sort order of terms will not.

The script does not create `output/tf/` for you. If the directory is missing, the `open` fails silently under default Perl (no `autodie`) and you get no tf files.

### Corpus df / idf

After every file:

```perl
my $n = $#files;
```

`$#files` is the last index of `@files`, not `scalar(@files)` and not “number of `.txt` files.”

If `gutenberg/` contains `.`, `..`, and 18 texts, then `@files` has 20 entries and `$n` is **19**. The mathematically intended \(N\) for this collection is **18**.

The committed `output/idf.txt` / `output/tfidf/` snapshot behaves like \(N = 18\): terms that appear in every book have idf `0` (see `a`, `about`, `after` in Alice). That is \(\ln(18/18)\), not \(\ln(19/18)\). Treat the checked-in tables as a teaching snapshot and treat `$n = $#files` as a historical off-by-one-plus-dots bug if you re-run.

df output header:

```text
word \t #docs it exists in \t doc names
```

Each data row is `term`, integer df, then filenames joined with `", "`. The trailing comma-space is leftover from the inner loop; it is harmless.

idf output is `term\tvalue` with

```perl
my $idf_val = log($n/($#vals+1));
```

Perl `log` is natural log. `$#vals+1` is the document frequency (last index + 1 of the filename list). If `$n` were ever smaller than df — it should not be — `log` of a fraction `< 1` would go negative. With the extra `.` / `..` in `$n`, idf is slightly larger than \(\ln(18/\mathrm{df})\) for every term.

## Stage 2: `tf*idf-product.pl`

This script is only a join and a multiply. It depends on [Text::CSV_XS](https://metacpan.org/pod/Text::CSV_XS) configured as a **tab** parser:

```perl
use Text::CSV_XS;
my $csv = Text::CSV_XS->new({sep_char => "\t"});
```

Why a CSV parser for two-column TSV? Terms are single tokens with no tabs after stage 1, so a `split /\t/` would have been enough. The parser is what the original write-up used; leave it if you are comparing to old output.

### Load idf

The entire `output/idf.txt` file is read into `%idf`. There is no header row in that file, so every line is a term.

If a tf file later contains a term missing from `%idf` (you edited one side by hand), Perl multiplies by `undef` and the product becomes `0` with a warning under `warnings` — but this script does not enable `warnings`.

### Per-file product

`readdir` on `output/tf`, skip `/^\./`, parse each line, multiply column 2 by `%idf{column 0}`, store in `%tfidf`, write `output/tfidf/$f` sorted by term.

Parse failures print `Error: ` plus `error_input` and skip that line. A typical failure is a stray blank line.

The output `open` is never explicitly `close`d. Perl closes it when the handle is reused or when the process exits. Fine for 18 files; sloppy if you wrap this in a long-running loop.

## What the scripts will not do

- They will not recurse into subdirectories.
- They will not skip `_` or `LICENSE` files; any non-dot filename in `gutenberg/` is a document.
- They will not lowercase the **filename**. `Alice.txt` and `alice.txt` would be two documents on a case-sensitive disk.
- They will not rebuild df if you delete one tf file and rerun only the product script. Stage 2 never recomputes idf.
- They will not compute cosine similarity, query ranking, or a single “top terms for the corpus” table. Use `examples/top_terms.py` on a tfidf file for the last of those.

## Re-running without clobbering the snapshot

The checked-in `output/` directory is part of the original toy example. To experiment:

```bash
mkdir -p /tmp/tfidf-scratch/{tf,tfidf}
# either copy the scripts and point them at new paths, or
# move the snapshot aside first
mv output output.snapshot
mkdir -p output/tf output/tfidf
perl tf-idf-values.pl
perl 'tf*idf-product.pl'
```

Restore `output.snapshot` if you want the committed numbers back.

The Python tiny-corpus tool writes under `examples/tiny-corpus/output/` by default so it cannot overwrite the Gutenberg snapshot.

## Mapping Perl hashes to the formulas

| Formula | Perl |
| --- | --- |
| \(\mathrm{count}(t, d)\) | `$tf{$d}` inside the per-file loop (the hash key is the term; `$d` is a token) |
| \(\lvert d \rvert\) | `$word_count` (includes empty split fields) |
| \(\mathrm{tf}(t, d)\) | `$tf{$t}/$word_count` |
| \(\mathrm{df}(t)\) | `$#vals+1` where `@vals = keys %{ $df{$t} }` |
| \(N\) | intended: count of non-dot files; actual: `$#files` |
| \(\mathrm{idf}(t)\) | `log($n/($#vals+1))` |
| \(\mathrm{tfidf}(t, d)\) | `$cols[1] * $idf{$cols[0]}` in the product script |

Variable reuse is the easy way to misread the first script: `$d` is a token in the inner loop and `$f` is a filename. The df key order is `$df{$d}{$f}`, term then file.

## Minimal rewrite checklist

If you reimplement stage 1 (the Python example already did this for a small folder):

1. Decide \(N = \) number of documents you actually scored.
2. Decide whether empty tokens belong in the tf denominator.
3. Write TSV sorted by term if you want `diff` against `output/`.
4. Keep natural log and no `+1` smoothing if you want the same ranking shape as the blog-era scripts.
5. Keep presence-only df (a set of filenames), not summed counts.

Do not “fix” the Gutenberg snapshot in place just to change \(N\). The snapshot is historical. Fix \(N\) in new code and say so, as `examples/tiny-corpus/compute_tfidf.py` does.
