# The original Perl pipeline

The 2012 snapshot is two scripts and a lot of TSV. This note is a reading of those scripts, not a rewrite of them.

## Pass 1: `tf-idf-values.pl`

The script:

1. `readdir`s `gutenberg/`
2. Skips any name that starts with `.`
3. Tokenizes each remaining file
4. Writes `output/tf/<filename>`
5. After the loop, writes `output/df.txt` and `output/idf.txt`

### Tokenization

For each line:

```perl
chomp($txt);
$txt =~ s/[\h\v]+/ /g;
$txt =~ tr/[A-Z]/[a-z]/;
$txt =~ s/[^a-zA-Z\d\s]//g;
my @data = split(/ +/, $txt);
```

In order:

1. Drop the newline.
2. Collapse horizontal and vertical whitespace runs to a single space.
3. Lowercase ASCII letters. The `tr/[A-Z]/[a-z]/` character class includes the brackets, but `[` maps to `[` and `]` maps to `]`, so the net effect is still A–Z → a–z.
4. Delete every character that is not a letter, digit, or whitespace.
5. Split on one or more spaces.

Then, for each field from `split`:

```perl
$word_count++;
if($d ne "")
{
    $tf{$d}++;
    $df{$d}{$f}=1;
}
```

Two details hide here.

**Empty tokens count toward `$word_count`.** `split(/ +/, " hello")` in Perl returns `("", "hello")`. The empty string is not added to `%tf`, but it still increments the denominator used for `tf = count / word_count`. Leading spaces after whitespace collapse therefore slightly shrink every `tf` in that document.

**Document frequency is a set.** `$df{$d}{$f}=1` records "token `d` occurs in file `f`." Later, `keys %{ $df{$t} }` is the posting list.

### Normalized TF output

```perl
print OUT $t."\t".($tf{$t}/$word_count)."\n";
```

Keys are sorted, so each `output/tf/` file is alphabetical, not ranked. Values are raw Perl floats.

### IDF and the `N` bug

```perl
my $n = $#files;
...
my $idf_val = log($n/($#vals+1));
```

`$#files` is the last index of the `readdir` array, not the number of documents processed. `readdir` includes `.` and `..`, and the original tree also had `.DS_Store`. The 2012 follow-up commit, `b50ebb9`, is titled "Bugfix: correcting idf values in calculating number of files" and rewrites the committed `idf` / `tfidf` tables.

The committed tables match `N = 18` (the number of `.txt` books), i.e. `ln(18 / df(t))`. The script on disk still assigns `$n = $#files`. If you rerun the Perl today on a clean directory listing, your `idf` values will not match `output/idf.txt` unless that last-index accident again equals 18.

The Python rewrite counts documents it actually tokenized.

## Pass 2: `tf*idf-product.pl`

This script does not reread the books. It:

1. Loads `output/idf.txt` as a hash
2. Reads every `output/tf/<file>`
3. Writes `output/tfidf/<file>` as `token\ttf * idf`

It parses TSV with `Text::CSV_XS` configured as `sep_char => "\t"`. That dependency is why the Python tools exist: they do the same join with the standard library.

The product files are also alphabetical, not ranked. `examples/python/rank_terms.py` is the ranking step the original snapshot never committed.

## What the scripts do not do

- They do not skip Gutenberg boilerplate.
- They do not drop numbers.
- They do not stem.
- They do not maintain a stopword list.
- They do not write a combined vocabulary index.
- They do not compute similarity. The blog post's next step (document vectors and a dot product) is implemented in [../examples/python/similarity.py](../examples/python/similarity.py) and described in [06-document-vectors-and-similarity.md](06-document-vectors-and-similarity.md).

## Re-running

```bash
# Requires perl and Text::CSV_XS. Overwrites output/.
perl tf-idf-values.pl
perl 'tf*idf-product.pl'
```

Prefer the Python path if you want a rerun that matches the documented `N = 18` rule and does not need CPAN modules:

```bash
python3 examples/python/run_pipeline.py --input gutenberg --output /tmp/gutenberg-tfidf
```
