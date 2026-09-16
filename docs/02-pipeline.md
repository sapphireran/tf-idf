# Pipeline

Two Perl scripts, three output layers, no database. You run them
from the repository root. They assume `gutenberg/` already holds
the texts and that `output/tf/` and `output/tfidf/` exist.

```text
gutenberg/*.txt
        │
        ▼
tf-idf-values.pl
        │
        ├── output/tf/<file>     one row per term:  term<TAB>tf
        ├── output/df.txt        term, df, comma-separated file names
        └── output/idf.txt       term<TAB>idf
                │
                ▼
        tf*idf-product.pl
                │
                └── output/tfidf/<file>   term<TAB>(tf * idf)
```

The checked-in `output/` is the result of that pair of scripts on
the 18 Gutenberg files. Re-running today will not reproduce those
IDF numbers exactly unless you fix `N`; see the last section.

## What you need

- `tf-idf-values.pl` uses only core Perl (`strict`, `opendir`,
  `open`).
- `tf*idf-product.pl` uses `Text::CSV_XS` with `sep_char => "\t"`
  to read the TF and IDF tables. That module is **not** in this
  environment by default. The tiny-corpus Python runner does not
  need it.

If you want to regenerate Gutenberg scores without the XS module,
`examples/tiny-corpus/run_tfidf.py` is the readable form of the
math. Pointing it at 18 novels is possible but not what it is
written for; it loads each file into memory the same way the Perl
does.

## Script 1: `tf-idf-values.pl`

For every name in `gutenberg/` that does not start with `.`:

1. Read the whole file into an array of lines.
2. Tokenize each line (whitespace collapse, lowercase, strip
   punctuation, split on spaces).
3. Count tokens in `%tf` and remember `{term -> {filename -> 1}}`
   in `%df`.
4. Write `output/tf/<filename>` with **normalized** TF,
   `count / word_count`, one term per line, sorted by term.

After the loop it writes the global tables:

- `output/df.txt` — header row, then `term`, document count, and
  the file names joined with `", "`.
- `output/idf.txt` — `term` and `log($n / df)`. Perl's `log` is
  natural log.

Dotfiles are skipped as documents (so `.DS_Store` is not scored)
but they still sit in the `@files` array that `readdir` returned.
That matters for `$n`.

## Script 2: `tf*idf-product.pl`

1. Load every IDF row into `%idf`.
2. For each file in `output/tf/`, multiply the TF by the IDF of
   that term.
3. Write `output/tfidf/<filename>` as `term<TAB>product`, sorted
   by term — **not** by score.

There is no ranking step in Perl. Alphabetical output is why you
need `examples/rank_terms.py` or `sort -g` to see what the score
thinks is important.

The product script opens an output handle per file and does not
call `close(OUT)` before the next file. On this corpus it still
flushes; it is just something to know if you adapt the script.

## File formats

All tables are tab-separated text. Terms are the first column.
There is no quoting unless `Text::CSV_XS` decides a field needs
it; the current output files are plain `term\tscore` rows.

```text
# output/tf/carroll-alice.txt
alice   0.0144867549668874
the     0.0612959060806743

# output/idf.txt
alice   1.79175946922805
the     0

# output/tfidf/carroll-alice.txt
alice   0.025956780390307
the     0
```

`output/df.txt` is the only file with a header and a third column.
`output/df-sorted.txt` is a derived listing of the same DF table.

## Corpus on disk

`gutenberg/` is 18 public-domain texts plus a `.DS_Store`. Sizes
are the checked-in files, not Project Gutenberg's current HTML
editions.

| File | Work | Size |
| --- | --- | ---: |
| `blake-poems.txt` | William Blake, *Songs of Innocence and of Experience* (and *The Book of Thel*) | 38 KB |
| `burgess-busterbrown.txt` | Thornton W. Burgess, *The Adventures of Buster Bear* | 85 KB |
| `shakespeare-macbeth.txt` | *Macbeth* | 100 KB |
| `shakespeare-caesar.txt` | *Julius Caesar* | 112 KB |
| `carroll-alice.txt` | Lewis Carroll, *Alice's Adventures in Wonderland* | 144 KB |
| `shakespeare-hamlet.txt` | *Hamlet* | 163 KB |
| `bryant-stories.txt` | Sara Cone Bryant, *Stories to Tell to Children* | 249 KB |
| `chesterton-thursday.txt` | G. K. Chesterton, *The Man Who Was Thursday* | 321 KB |
| `chesterton-brown.txt` | G. K. Chesterton, *The Wisdom of Father Brown* | 407 KB |
| `chesterton-ball.txt` | G. K. Chesterton, *The Ball and the Cross* | 457 KB |
| `austen-persuasion.txt` | Jane Austen, *Persuasion* | 466 KB |
| `milton-paradise.txt` | John Milton, *Paradise Lost* | 468 KB |
| `austen-sense.txt` | Jane Austen, *Sense and Sensibility* | 673 KB |
| `whitman-leaves.txt` | Walt Whitman, *Leaves of Grass* | 711 KB |
| `austen-emma.txt` | Jane Austen, *Emma* | 887 KB |
| `edgeworth-parents.txt` | Maria Edgeworth, *The Parent's Assistant* | 935 KB |
| `melville-moby_dick.txt` | Herman Melville, *Moby-Dick* | 1.2 MB |
| `bible-kjv.txt` | King James Bible | 4.3 MB |

Together they produce 57,368 distinct terms. Alice's TF table has
2,753 rows; Moby-Dick has 19,961; the Bible has 16,567. The Bible
is longer but more repetitive, so Melville still wins on vocabulary
size.

## The `N` used for IDF

In `tf-idf-values.pl`:

```perl
my @files = readdir(DIR);
# ...
my $n = $#files;    # last index, i.e. scalar(@files) - 1
```

`readdir` includes `.` and `..`. This directory also has
`.DS_Store`. A fresh run would set `$n` to something other than 18.

The **checked-in** `output/idf.txt` was computed with **N = 18**:

```text
idf("macbeth") = 2.89037175789616 = ln(18)
idf("alice")   = 1.79175946922805 = ln(18/3)
idf("the")     = 0                = ln(18/18)
```

So the published scores match "one IDF weight per `.txt` book".
The tiny-corpus runner uses that definition on purpose:
`n = len(docs)` after skipping dotfiles.

If you regenerate Gutenberg output and your top terms shift a
little, check `$n` before you debug the tokenizer.

## What the scripts do not do

- They do not download Gutenberg. The texts are already in the repo.
- They do not stem, lemmatize, or drop stopwords. Stopwords die
  from IDF = 0 when they are truly global, not from a stoplist.
- They do not emit a ranked view. Ranking is a later, separate
  step.
- They do not treat the three Austen novels as one author cluster,
  or the three Shakespeare plays as one cluster. Each file is its
  own document. That is why `emma` is rare and `the` is not, and
  why `haue` (old spelling of *have*) becomes a Shakespeare
  marker instead of disappearing as a stopword.
