# Script reference

A reading guide for the two original Perl programs. Line numbers refer to the versions in this tree.

## `tf-idf-values.pl`

Purpose: one pass over `gutenberg/`, write per-document tf and collection-wide df/idf.

### Setup

```perl
use strict;
opendir(DIR,"gutenberg");
my @files = readdir(DIR);
my %df;
```

`%df` is a HoH: `$df{$term}{$filename} = 1`. Using a hash as a set is how df becomes “number of documents,” not “number of occurrences.”

### Per-document loop

Dotfiles are skipped with `if($f !~ /^\./)`. That skips `.` and `..` and would also skip a `.DS_Store` inside `gutenberg/` (the committed `.DS_Store` sits at the repo root, not in the corpus directory).

Cleaning, in order:

1. `chomp` — drop the record separator.
2. `s/[\h\v]+/ /g` — Unicode-aware horizontal and vertical whitespace become a single space. Newlines already `chomp`ed still matter if a line held only `\r` or odd blanks.
3. `tr/[A-Z]/[a-z]/` — lowercase. The character-class brackets are included in the transliteration sets; they map to themselves and are then stripped.
4. `s/[^a-zA-Z\d\s]//g` — keep letters, digits, whitespace.
5. `split(/ +/)` — one or more spaces.

Each field increments `$word_count`. Only non-empty fields increment `$tf{$d}` and mark `$df{$d}{$f}`.

### Writing `output/tf/$f`

```perl
print OUT $t."\t".($tf{$t}/$word_count)."\n";
```

Division is ordinary Perl NV (double). There is no rounding. Terms are `sort keys %tf` (ASCII / Unicode code-point order on the lowercased keys).

The handle is closed per file.

### Global df / idf

```perl
my $n = $#files;
```

Last index of the `readdir` array. See [known-quirks.md](known-quirks.md).

```perl
my $idf_val = log($n/($#vals+1));
```

`log` in Perl is the natural logarithm. `$#vals+1` is `scalar @vals`, the document frequency.

`output/df.txt` gets a human header and a trailing `", "` after every filename, including the last.

`output/idf.txt` has no header.

Division by zero cannot happen: a term exists in `%df` only if it appeared in at least one document, so `@vals` is never empty.

## `tf*idf-product.pl`

Purpose: join tf tables to the global idf table.

### Idf load

```perl
use Text::CSV_XS;
my $csv = Text::CSV_XS->new({sep_char => "\t"});
# ...
$idf{$cols[0]} = $cols[1];
```

Column 0 is the term, column 1 is the weight. No header is expected.

If a term in a tf file is missing from `%idf`, Perl multiplies by `undef`, warns under `use warnings` (this file does not enable warnings), and treats the missing idf as 0. Every term written by `tf-idf-values.pl` should exist in `idf.txt`, so this is a consistency check more than a feature.

### Per-tf-file product

```perl
my $val = $cols[1] * $idf{$cols[0]};
$tfidf{$cols[0]} = $val;
```

Parse errors print `Error: $csv->error_input` and skip the row.

Output is again `sort keys`, tab, number, newline. The script does not create `output/tfidf/` for you; the directory must already exist (it does in the committed tree).

### Why TSV-as-CSV

The original author used `Text::CSV_XS` for a two-column tab file. That is robust if a term ever contained a tab (it cannot, given the tokenizer) and is the only CPAN dependency in the repo.

## Suggested reading order

1. Skim [tf-idf-explained.md](tf-idf-explained.md) so the two writes make sense.
2. Read `tf-idf-values.pl` top to bottom (it is ~70 lines).
3. Read `tf*idf-product.pl` (~50 lines).
4. Run `python3 examples/run_toy_example.py` and compare every printed number to [../examples/worked-example.md](../examples/worked-example.md).
5. Only then trust a ranking from `output/tfidf/`.

## If you extend the scripts

Keep changes in the example helpers unless you are deliberately replacing the 2012 toy. Useful extensions that do **not** belong in a silent rewrite of the originals:

- Count \(N\) as “files actually parsed.”
- Close the tf-idf output handle each iteration.
- Write scores sorted by weight, or write both an alpha file and a ranked file.
- Drop a tiny stopword list *after* showing the idf=0 effect, not before.
- Emit UTF-8 explicitly.

`examples/tfidf_mini.py` is the place to try those variations.
