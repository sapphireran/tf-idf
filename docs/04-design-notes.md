# Design notes

The Perl scripts are a blog-post toy. They do a few things that a
modern IR stack would not, and those choices leak into the scores.
This page lists the ones that showed up while documenting the
checked-in `output/`.

## Tokenization is punctuation deletion, not splitting

After lowercasing, every character outside `[a-zA-Z0-9]` and
whitespace is deleted. A comma or dash does **not** become a
boundary.

```text
"adventures beginning"   -> adventures, beginning
"adventures,beginning"   -> adventuresbeginning
"whale-the"              -> whalethe
"don't"                  -> dont
"Alice's"                -> alices
```

The Alice TF-IDF table contains `adventuresbeginning`, `themand`,
and `alices`. The IDF table contains `whalethe`, `whalethis`,
`thethe`. Those are not OCR errors in every case; many are two
words that only had punctuation between them.

The tiny corpus avoids hyphens so the worked example stays
countable. If you add `moth-shadow` to `cats.txt` it becomes the
new term `mothshadow` and does not increment `moth`.

## Empty tokens still lengthen the document

```perl
$word_count++;
if($d ne "") {
    $tf{$d}++;
    $df{$d}{$f}=1;
}
```

`word_count` is the denominator of TF. Empty strings from
`split(/ +/, ...)` count toward length and never become terms.
Blank lines are fine (`split` on `""` yields no tokens). A line
that is only spaces can produce an empty token and inflate
`word_count` by one.

On Gutenberg prose this is noise. On a file of decorative
punctuation it would drag every TF down.

## `N` is `$#files`, not the number of scored documents

```perl
my @files = readdir(DIR);
my $n = $#files;
```

`$#files` is `scalar(@files) - 1`. `readdir` always includes `.`
and `..`. This tree also has `gutenberg/.DS_Store`, which is
skipped as a document (name starts with `.`) but still occupies a
slot in `@files`.

The published IDF table was built with **N = 18**:

```text
ln(18/1) = 2.89037175789616   # macbeth
ln(18/3) = 1.79175946922805   # alice
ln(18/18) = 0                 # the
```

A re-run with the current directory listing will use a different
`N` and every IDF row will move. The tiny-corpus runner counts
processed documents instead, which is the definition the published
Gutenberg numbers already satisfy.

The historical commit message "correcting idf values in calculating
number of files" is the reason `$n = $#files` is there. Treat the
checked-in `output/` as the reference snapshot; do not expect a
bit-identical regenerate until `N` is computed from the same set
of non-dot `.txt` files.

## No stopword list, no stemmer

Function words disappear only when `df = N`. On this folder that
is 221 terms, including `a` and `the`.

Function words that are *not* in every file keep a residual IDF.
Shakespeare's `haue`, `vpon`, and `vs` are everyday words in 1606
and rare in 19th-century novels, so they rank like content.
Austen's `mr` / `mrs` survive for the same reason: Burgess and
Blake do not write that way.

There is also no stemmer, so `whale` and `whales` are two terms
(and both appear in the Moby-Dick top ten). `weep` and `weeping`
both show up for Blake.

## Speech prefixes look like brilliant keywords

The Shakespeare files are plays. `macb`, `macd`, `ham`, `hor`,
`pol` are speaker labels printed on hundreds of lines. They are
unique to that file and extremely frequent, which is the TF-IDF
jackpot.

If you want a reading list of *themes*, strip prefixes first. If
you want a demo of "the scorer believes the markup", leave them
in. This repo leaves them in.

## `sort -n` lies about scientific notation

GNU `sort -n` parses `9.89346416555399e-05` as `9.893...` and
stops at `e`. A descending numeric sort then promotes mid-list
Alice words (`get`, `party`, `nose`) over `alice` (0.026).

Use one of:

```bash
sort -t$'\t' -k2,2g output/tfidf/carroll-alice.txt | tail
python3 examples/rank_terms.py output/tfidf/carroll-alice.txt
```

`-g` is general numeric sort. `rank_terms.py` uses Python `float`,
which understands `e-05`.

## The product script depends on `Text::CSV_XS`

`tf*idf-product.pl` parses tabs with `Text::CSV_XS`. The first
script does not. A machine with only core Perl can rebuild TF, DF,
and IDF but cannot rebuild `output/tfidf/` without that module or
a one-line rewrite to `split(/\t/)`.

The TSV rows in this repo do not need a CSV parser. They are one
term, one tab, one number.

## Cross-file leakage is a feature

`alice` appears in *The Man Who Was Thursday* and *The Parent's
Assistant*, so Carroll does not get the maximum IDF. `ahab` appears
in the KJV. `whale` appears in six files.

That leakage is the method working. The folder is the universe.
Add or drop a book and every weight changes. There is no global
English background corpus.

## What I would change in a second toy, and did not change here

The original scripts stay as they were. The docs and the tiny
corpus describe them. A follow-up toy, if I ever write one, would:

1. Set `N` to the count of processed non-dot files.
2. Replace punctuation with spaces instead of deleting it.
3. Drop speaker-prefix lines in the plays, or split them off.
4. Rank TF-IDF in the product script (or write a third script).
5. Close the per-file output handle.
6. Skip `Text::CSV_XS` for two-column TSV.

None of that is required to understand the blog-post numbers, which
is why it is not in the Perl.
