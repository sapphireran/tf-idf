# Algorithm

This note describes the formulas **as the two root scripts implement them**, not a textbook variant. The tiny runner in `examples/toy-tfidf.pl` uses the same tokenization and the same `ln(N / df)` IDF, but it takes `N` as the number of processed documents. The Gutenberg script's `N` is slightly different; see [Collection size N](#collection-size-n).

## Pipeline

```text
gutenberg/*.txt
        │
        ▼
 tokenize, lowercase, strip punctuation
        │
        ├──► output/tf/<file>          TF(t, d) = count(t, d) / |d|
        ├──► output/df.txt             df(t) and the file names that contain t
        └──► output/idf.txt            idf(t) = ln(N / df(t))
                │
                ▼
        output/tfidf/<file>            tfidf(t, d) = TF(t, d) × idf(t)
```

`tf-idf-values.pl` produces the TF, DF, and IDF tables. `tf*idf-product.pl` only multiplies.

## Tokenization

Each input line is normalized in this order:

1. Strip the trailing newline (`chomp`).
2. Collapse horizontal and vertical whitespace runs to a single space: `s/[\h\v]+/ /g`.
3. Lowercase ASCII letters: `tr/[A-Z]/[a-z]/`.
4. Delete every character that is not a letter, digit, or whitespace: `s/[^a-zA-Z\d\s]//g`.
5. Split on one or more spaces.

Empty tokens after the split are not stored in the TF or DF maps, but they still increment the document's raw `word_count`. That means a line that becomes only spaces after punctuation stripping dilutes every TF value in that document by a tiny amount.

Consequences you will see in the Gutenberg tables:

- Apostrophes disappear, so `Alice's` becomes `alices` and `don't` becomes `dont`.
- Hyphenated compounds become one token (`nantucket` stays; `sperm-whale` becomes `spermwhale` if written with a hyphen).
- Shakespeare spellings stay as they appear after the strip (`haue`, `loue`, `selfe`).
- Speaker prefixes in the play texts (`HAM.`, `HOR.`) become short tokens (`ham`, `hor`) and dominate that document's ranking.

The toy runner copies these rules so a worked example and a Gutenberg rerun stay comparable.

## Term frequency

For each processed file `d` and token `t`:

```text
TF(t, d) = count(t, d) / word_count(d)
```

`word_count(d)` is the number of split fields, including empty ones. `count(t, d)` counts only non-empty tokens.

TF tables are written as `token<TAB>probability`, one token per line, sorted by token. Values are ordinary Perl floating-point numbers, not rounded.

A word that appears once in a short poem therefore has a much larger TF than a word that appears once in `bible-kjv.txt`.

## Document frequency

`df(t)` is the number of **files** in which `t` occurs at least once. The scripts do not weight by how often the word appears inside those files.

`output/df.txt` records both the count and the file names:

```text
word<TAB>#docs it exists in<TAB>doc names
alice	3	carroll-alice.txt, chesterton-thursday.txt, ...
```

The header line is prose, not a machine schema. Skip it when parsing.

## Inverse document frequency

```text
idf(t) = ln(N / df(t))
```

`ln` is the natural logarithm (`log` in Perl). There is no smoothing: a word that appears in every counted document gets `ln(1) = 0`. There is no `+1` in the numerator or denominator.

Because IDF is zero for collection-wide words, their TF-IDF is zero in every file even when TF is large. That is why `the` and `and` vanish from the ranked lists.

### Collection size N

`tf-idf-values.pl` sets

```perl
my $n = $#files;
```

`@files` is the raw `readdir` list, which includes `.` and `..`. `$#files` is the last index, so `N` is `readdir_count - 1`, not the number of processed `.txt` files.

The committed `output/idf.txt` snapshot was produced when that expression evaluated to **18**, matching the 18 Gutenberg texts. A fresh run on a directory that also contains `.` and `..` (and nothing else) yields `N = 19`. IDF values will then differ slightly from the committed tables.

`examples/toy-tfidf.pl` documents this and uses `N = number of processed documents` so the worked example stays stable.

## TF-IDF

```text
tfidf(t, d) = TF(t, d) × idf(t)
```

The product script reads `output/idf.txt` into a hash, then for each `output/tf/<file>` writes `output/tfidf/<file>`. Tokens that appear in a TF table but are missing from the IDF hash multiply as if IDF were `undef` (Perl treats that as `0` in numeric context).

Rows are sorted by token, not by score. Use `examples/top-terms.pl` to rank them.

## What this is not

- Not BM25, not sublinear TF (`1 + ln(tf)`), not cosine-normalized document vectors.
- Not a stop-word list. Stop words disappear only because IDF hits zero.
- Not language-aware. There is no stemmer and no sentence splitter.
- Not streaming. Each document is read into an array of lines.

Those omissions are intentional. The point of the project is to watch every intermediate table on a small public-domain collection.
