# Tokenizer and other quirks

The 2012 scripts are short and literal. This page records the behavior the
examples depend on, including the bits you would change in a production indexer.

## Tokenization (`tf-idf-values.pl`)

For each line:

1. `chomp` the newline.
2. Collapse horizontal/vertical whitespace: `$txt =~ s/[\h\v]+/ /g`.
3. Lowercase with `tr/[A-Z]/[a-z]/`.
4. Delete every character that is not ASCII letter, digit, or whitespace:
   `$txt =~ s/[^a-zA-Z\d\s]//g`.
5. `split(/ +/, $txt)` on one or more spaces.

A token is kept if it is not the empty string. There is no stop list, no
Unicode letter class, and no stemmer.

### What this does to real text

| Original | Tokens |
| --- | --- |
| `Hello, Emma!` | `hello`, `emma` |
| `Emma's` | `emmas` (apostrophe deleted, letters join) |
| `whale-ship` | `whaleship` (hyphen deleted) |
| `28th-and` | `28thand` (seen in *Emma*'s TF table) |
| `"Pipe a song about a Lamb!"` | `pipe`, `a`, `song`, `about`, `a`, `lamb` |
| `MACB.` / `Macb.` | `macb` |
| `100.00` | `10000` (dot deleted) |
| accented or curly quotes | stripped or broken; input here is mostly ASCII |

The tiny-corpus Python scorer copies this ASCII rule so its numbers stay
aligned with the prose in [`../examples/hand-calculation.md`](../examples/hand-calculation.md).

### `$word_count` vs. kept tokens

```perl
$word_count++;
if($d ne "")
{
    $tf{$d}++;
    $df{$d}{$f}=1;
}
```

Empty pieces from `split` still increment `$word_count`. Relative TF is then
slightly smaller than `count / (kept tokens)`. On the cleaned tiny documents
the two denominators match. On Gutenberg they can drift on blank or
punctuation-only lines.

## Document frequency is a set, not a counter of mentions

`$df{$term}{$filename} = 1` means “seen in this file.” A thousand `whale`s in
*Moby-Dick* add one to `df(whale)`, the same as a single `whale` in *Hamlet*.

## IDF uses `log` (natural log) and a fragile `N`

```perl
my $n = $#files;
my $idf_val = log($n/($#vals+1));
```

- `log` is `ln`.
- `$#vals+1` is the DF (last index + 1 of the filename list).
- `$#files` is **not** “number of `.txt` files.” See [`pipeline.md`](pipeline.md).

Checked-in tables: `N = 18`.

## Files the first script will try to read

`readdir` + “skip names starting with `.`” still picks up:

- `gutenberg/.DS_Store` (present in this checkout)
- any future `README.txt` you drop in that folder
- backup files that do not start with a dot

Only `*.txt` literary files belong in a clean run.

## Second script depends on `Text::CSV_XS`

`tf*idf-product.pl` will not start without that XS module. The data is simple
tab-separated text; a `split /\t/, $line, 2` would have been enough. The
dependency is historical.

It also never `close`s the per-file `OUT` handle. Harmless for 18 files;
sloppy if you pointed it at thousands.

## Output is alphabetical, scores are floats-as-text

Do not eyeball “top terms” by opening the file. Use a numeric sort or
`examples/rank_top_terms.py`.

Perl's default float stringification produced values like `2.89037175789616`
and `1.26441432328545e-05`. Python `float()` reads them. A trailing non-numeric
character will not.

## Known dirty row: `thatyou`

`output/idf.txt` line 50450:

```
thatyou	2.89037175789616y
```

The term itself is a glued token (`that` + `you`). The extra `y` on the number
looks like a one-off edit artifact. DF for `thatyou` is 1 (singleton IDF), so
the intended value is `ln(18)`.

Leave the row in place; it is part of the historical output. The ranker script
strips a trailing junk character if `float()` fails.

## Why *Emma*'s top TF-IDF list is names, not themes

The tokenizer does not know that `Emma`, `Miss Woodhouse`, and `she` are the
same entity. It also does not know that `Hartfield` is a house. TF-IDF then
does exactly one thing: reward strings that repeat in one file and are scarce
elsewhere. In a novel, that is almost always the cast list.

## Why Shakespeare lists look “misspelled”

The source files use old spelling and abbreviated speech headings. After the
tokenizer, those are just high-TF, often high-IDF unigrams. Cleaning them
would be a different project (modernization, speaker-tag stripping). The
example in [`../examples/shakespeare-speaker-tags.md`](../examples/shakespeare-speaker-tags.md)
keeps them so the effect is visible.

## What I am not changing

The Perl scripts stay in their 2012 form. New work lives under `docs/` and
`examples/`, including a Python scorer that makes `N` explicit and writes the
same TSV shape.
