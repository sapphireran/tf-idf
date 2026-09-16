# TF-IDF as this repo computes it

This note is a personal walkthrough of the arithmetic behind the 2012
Perl scripts and the Python benchmark. It is not a survey of every
weighting scheme in IR. The only formula that matters for reproducing
`output/` is the one below.

## The three counts

Treat each file in `gutenberg/` as one document. After tokenization
(see below) you have, for every term `t` and document `d`:

| Symbol | Meaning in this repo |
| --- | --- |
| `count(t, d)` | How many times `t` occurs in `d` |
| `word_count(d)` | How many split fields `d` contributed, including empties |
| `df(t)` | How many documents contain `t` at least once |
| `N` | How many documents are in the collection |

From those:

```
tf(t, d)   = count(t, d) / word_count(d)
idf(t)     = ln(N / df(t))
tfidf(t,d) = tf(t, d) * idf(t)
```

`ln` is the natural logarithm. Perl's `log` and Python's `math.log`
both default to that base. Changing the base multiplies every IDF by
a constant and does not change the ranking inside a single document.

### Why divide by `word_count`

A 4 MB Bible and a 38 KB Blake file are not the same length. Raw
counts would make every common word in the Bible look "important"
just because the book is long. Dividing by the document's token
count turns TF into a share of that document.

### Why IDF uses a logarithm

`N / df` is already "rarer is larger": a term in one of 18 books
scores 18, a term in all 18 scores 1. The log compresses that range
(`ln(18) ≈ 2.89`, `ln(1) = 0`) and is the conventional Sparck-Jones
form. The important qualitative effect is the zero: a term that
appears in every document is thrown away for free, without a
stop-word list.

### What this is not

Popular libraries often use a different IDF, for example sklearn's

```
idf(t) = ln((N + 1) / (df(t) + 1)) + 1
```

or a plus-one smooth `ln(N / (1 + df))`. Those do **not** match
`output/idf.txt`. The benchmark can print them for curiosity
(`--variant smooth` / `--variant sklearnish`) but the default
`--variant classic` is the 2012 formula.

There is also no BM25, no sublinear TF (`1 + ln(count)`), and no
cosine length-normalization of the TF-IDF vector. Adding any of
those would be a different experiment.

## Worked example (three tiny documents)

This is the same toy the benchmark uses for `--self-test`. Spaces
and punctuation are already gone; each line is one document.

```
doc_a: the cat sat
doc_b: the dog sat
doc_c: the cat
```

`N = 3`. Token counts:

| term | A | B | C | df |
| --- | --- | --- | --- | --- |
| the | 1 | 1 | 1 | 3 |
| cat | 1 | 0 | 1 | 2 |
| sat | 1 | 1 | 0 | 2 |
| dog | 0 | 1 | 0 | 1 |

Document lengths are 3, 3, and 2.

```
idf(the) = ln(3/3) = 0
idf(cat) = ln(3/2) ≈ 0.4054651081081644
idf(sat) = ln(3/2) ≈ 0.4054651081081644
idf(dog) = ln(3/1) ≈ 1.0986122886681098
```

TF-IDF for `cat` in `doc_a`:

```
tf(cat, A)    = 1/3
tfidf(cat, A) = (1/3) * ln(3/2) ≈ 0.1351550360360548
```

TF-IDF for `dog` in `doc_b`:

```
tf(dog, B)    = 1/3
tfidf(dog, B) = (1/3) * ln(3/1) ≈ 0.36620409622270325
```

`the` is zero in every document. That is the whole IDF trick on a
postcard: the word is frequent inside each file **and** frequent
across files, so it cannot distinguish anything.

`--self-test` recomputes these four IDF values and the two TF-IDF
cells above and exits non-zero if they drift.

## Tokenizer pipeline (must match the Perl)

`tf-idf-values.pl` is not a Unicode-aware NLP tokenizer. For each
line it does, in order:

1. Drop the trailing newline (`chomp`).
2. Collapse Perl horizontal + vertical whitespace (`[\h\v]+`) to a
   single space. On this ASCII corpus that is the same as collapsing
   `[ \t\n\v\f\r]+`.
3. Map `A–Z` to `a–z` with `tr///`.
4. Delete every character that is not a letter, a digit, or
   whitespace: `s/[^a-zA-Z\d\s]//g`. Apostrophes, em-dashes, and
   Gutenberg page markers all disappear. `don't` becomes `dont`.
5. Split on one or more spaces.

Empty fields still happen at the ends of a line that had leading or
trailing whitespace. The Perl increments `word_count` for **every**
split field and only then skips empties when updating `%tf` and
`%df`:

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

So the TF denominator is slightly larger than "number of real
tokens" on any file whose lines pad with spaces. The checked-in
`output/tf/` tables were built with that denominator. The benchmark
copies the same order of operations so a comparison against those
tables is meaningful.

DF is a set of filenames per term (`$df{$term}{$filename} = 1`).
A word that occurs 400 times in *Moby-Dick* and nowhere else still
has `df = 1`.

## Choosing `N`

The IDF formula needs a collection size. There are two numbers you
might reasonably pick in this checkout:

| Mode | Value on this tree | What it matches |
| --- | --- | --- |
| `documents` | 18 | `output/idf.txt` (`ln(18/1) ≈ 2.89037`) |
| `perl-last-index` | `$#files` after `readdir` | A fresh run of `tf-idf-values.pl` |

`readdir` on `gutenberg/` includes `.`, `..`, and `.DS_Store`, so
`$#files` is 20 here (21 entries, last index 20). The 2012 tables
were clearly produced with `N = 18`: a singleton term has IDF
`2.89037175789616`, which is `ln(18)`, not `ln(20)` or `ln(21)`.

The benchmark defaults to `documents`. Use `--n-mode perl-last-index`
only when you are trying to shadow a live Perl run rather than the
checked-in files.

## Reading the output tables

All of the Perl tables are tab-separated, one term per line, terms
sorted lexicographically.

- `output/tf/<file>`: `term<TAB>tf`
- `output/idf.txt`: `term<TAB>idf`
- `output/tfidf/<file>`: `term<TAB>tf*idf`
- `output/df.txt`: `term<TAB>df<TAB>comma-separated filenames`

A TF-IDF of `0` means the term appears in every document, not that
the term is absent. Absence is simply a missing row: the per-document
files only list terms that occurred in that file.

Because terms are sorted by name, not by score, the "interesting"
words are not at the top of the file. The benchmark's `--top N`
listing is the easier way to look at a book.

## What a high score is telling you

A large `tfidf(t, d)` means:

- `t` takes up a real fraction of `d` (high TF), **and**
- `t` is missing from most of the other 17 books (high IDF).

That is why character names and topic nouns float up: `alice` is
common in one file and rare in the others; `whale` the same;
`macbeth` the same. It is also why a word that is rare everywhere,
including in `d`, does not automatically win — a single occurrence
in a long book is a tiny TF.

If you want a ranking you can read as "keywords for this book",
sort that book's TF-IDF table descending and ignore the zeros.
That is all the original blog post was demonstrating.
