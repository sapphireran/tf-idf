# Limitations and implementation quirks

This project is a personal blog-post toy. The list below is the set
of things the scores will not tell you, plus the places the original
Perl is slightly surprising.

## No stopword list

Collection-wide tokens get `idf = 0` and disappear from the useful
end of a ranking. Tokens that are common but not universal (`mr`,
`mrs`, `thou`, `have`) stay. If you want newspaper-style keywords
you still need an explicit stoplist or a higher `df` cutoff.

## No stemmer and no lemmatizer

`whale` and `whales` are different terms. Both appear in the
Moby-Dick top 12. `alice` and `alices` are different terms.
`anarchist` and `anarchists` both appear in the Thursday ranking.

## Punctuation is deleted, not turned into a boundary

The cleaner strips every non-alphanumeric character. Hyphens vanish
**between** letters, so `well-known` becomes `wellknown`.
Apostrophes vanish, so `o'er` becomes `oer` and `pass'd` becomes
`passd`.

That is why Folio spellings remain readable (`haue`) while
contractions become new types.

## Empty tokens can dilute Perl TF

In `tf-idf-values.pl`:

```perl
foreach my $d (@data)
{
    $word_count++;
    if($d ne "")
    {
        $tf{$d}++;
        $df{$d}{$f}=1;
    }
}
```

`word_count` increments before the empty-string check. A leading
space after whitespace-collapsing can produce an empty field from
`split(/ +/, ...)`. Those empties do not enter `%tf` but they do
enter the denominator.

The teaching Python counts only non-empty tokens by default and
exposes `--count-empty-tokens` if you want the Perl denominator.

On the Gutenberg files the effect is small. On a file of blank
lines it is not.

## `N` is easy to get wrong in the original script

```perl
my $n = $#files;
```

`$#files` is the last index of `readdir`, which includes `.` and
`..` and any other directory entry. The snapshot IDF table matches
`N = 18` (the `.txt` count), not a raw `readdir` length on a folder
that also has `.DS_Store`.

Re-running `tf-idf-values.pl` without fixing `N` will shift every
IDF. The teaching Python sets `N` to the number of processed files.

## Speech prefixes and stage markup are terms

Shakespeare files rank `ham`, `macb`, `bru`, `ophe`. Those are
speaker labels. TF-IDF is working. The input is a play script, not
a novelized text.

## Project Gutenberg headers are terms

`chesterton-ball.txt` ranks `ebook` and `gutenberg`. A unique
repeated header is a high-IDF, medium-TF token. Strip headers
before scoring if you care about narrative vocabulary.

The same leak produces the huge catalog-looking keys at the top of
`output/idf.txt` (`00021053`, `1001`, …). Those have maximum IDF
and tiny TF, so they rarely win a document ranking.

## Numbers and catalog ids are terms

The tokenizer keeps digits. Verse numbers, years (`1865` in the
Alice banner), and Gutenberg ids all enter the tables.

## Hash order in `df.txt`

Column 3 of `output/df.txt` is Perl hash key order from the original
run. Do not parse it as a stable ranking of files.

## TF-IDF is not a similarity

This repository never computes cosine similarity, query retrieval,
or clustering. You *can* treat each `output/tfidf/<file>` as a sparse
vector and compare books; that is extra work and not what the Perl
writes.

## Short documents are loud

TF is a share of the document. A 3-token file gives each token
`tf = 1/3`. See the bread document in [worked-example.md](worked-example.md).
Blake vs. the KJV is the same effect in the real snapshot.

## The collection is tiny

Adding a nineteenth file changes every IDF. Removing the Bible
changes Milton and Blake more than it changes Austen. Do not treat
`output/idf.txt` as a universal English rarity table.

## Float formatting is not a checksum

Perl and Python will not print identical decimal strings. Compare
rankings and reconstructed `df` values, or use the unit tests on the
micro collection.

## Historical scripts are not a library

`tf-idf-values.pl` and `tf*idf-product.pl` hard-code relative paths,
create no directories, and assume `gutenberg/` and `output/` already
exist. They are the blog-post calculation. New examples should go
through `examples/python/compute_tfidf.py`.

## Personal scope

This tree is personal study material: public-domain texts, personal
writeups, and a stdlib teaching implementation. It is not a place
for company documents or production ranking code.
