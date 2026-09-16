# tf-idf

Personal toy for scoring a folder of Project Gutenberg texts with
TF-IDF. It accompanies an old blog post. The math is the textbook
product

```text
tfidf(term, doc) = (count / doc_length) * ln(N / df)
```

with no stopword list, no stemmer, and no add-one smoothing. The
Perl in the root is the original. `docs/` and `examples/` are a
later write-up so I can come back to the output without re-deriving
every number.

## Layout

```text
tf-idf-values.pl      # TF per file, then DF and IDF for the folder
tf*idf-product.pl     # TF * IDF per file
gutenberg/            # 18 public-domain texts
output/               # checked-in snapshot of a full run
  tf/                 # term → normalized TF
  df.txt              # term → document count + file names
  idf.txt             # term → ln(N / df)
  tfidf/              # term → TF * IDF
docs/                 # how the score works and how to read output/
examples/             # tiny original corpus + a ranking helper
```

## Corpus

Eighteen files, one document each. Details and sizes are in
[docs/02-pipeline.md](docs/02-pipeline.md).

| File | Work |
| --- | --- |
| `austen-emma.txt` | Jane Austen, *Emma* |
| `austen-persuasion.txt` | Jane Austen, *Persuasion* |
| `austen-sense.txt` | Jane Austen, *Sense and Sensibility* |
| `bible-kjv.txt` | King James Bible |
| `blake-poems.txt` | William Blake, *Songs of Innocence and of Experience* |
| `bryant-stories.txt` | Sara Cone Bryant, *Stories to Tell to Children* |
| `burgess-busterbrown.txt` | Thornton W. Burgess, *The Adventures of Buster Bear* |
| `carroll-alice.txt` | Lewis Carroll, *Alice's Adventures in Wonderland* |
| `chesterton-ball.txt` | G. K. Chesterton, *The Ball and the Cross* |
| `chesterton-brown.txt` | G. K. Chesterton, *The Wisdom of Father Brown* |
| `chesterton-thursday.txt` | G. K. Chesterton, *The Man Who Was Thursday* |
| `edgeworth-parents.txt` | Maria Edgeworth, *The Parent's Assistant* |
| `melville-moby_dick.txt` | Herman Melville, *Moby-Dick* |
| `milton-paradise.txt` | John Milton, *Paradise Lost* |
| `shakespeare-caesar.txt` | *Julius Caesar* |
| `shakespeare-hamlet.txt` | *Hamlet* |
| `shakespeare-macbeth.txt` | *Macbeth* |
| `whitman-leaves.txt` | Walt Whitman, *Leaves of Grass* |

`output/idf.txt` has 57,368 distinct terms. 36,887 of them appear
in only one file. 221 appear in all eighteen and therefore have
IDF 0 (`the`, `a`, and friends).

## Run the original scripts

From the repository root, after `output/tf` and `output/tfidf`
exist:

```bash
perl tf-idf-values.pl
perl 'tf*idf-product.pl'
```

The second script needs `Text::CSV_XS`. The first does not. A
fresh run will not bit-match `output/idf.txt` unless `N` is 18;
the script currently sets `$n = $#files` after `readdir`, which
counts `.` / `..` / `.DS_Store`. The snapshot was computed with
N = 18. That discrepancy is documented in
[docs/04-design-notes.md](docs/04-design-notes.md).

You do not need to regenerate anything to read the results. The
snapshot is the point of the repo.

## Rank a result file

The Perl writes terms in alphabetical order. GNU `sort -n` misreads
`9.89e-05` as `9.89`. Use general numeric sort or the helper:

```bash
python3 examples/rank_terms.py output/tfidf/carroll-alice.txt -n 12
python3 examples/rank_terms.py output/tfidf/melville-moby_dick.txt \
    --versus output/tfidf/carroll-alice.txt
```

True peaks from the snapshot:

| File | Top terms |
| --- | --- |
| Alice | `alice`, `gryphon`, `dormouse`, `duchess`, `hatter` |
| Moby-Dick | `whale`, `ahab`, `sperm`, `stubb`, `queequeg` |
| Macbeth | `macb`, `haue`, `macbeth`, `macd` (prefixes + old spelling) |
| Emma | `emma`, `harriet`, `weston`, `knightley`, `elton` |
| Blake | `thel`, `weep`, `lyca`, `thee` |

The Macbeth row is the scorer doing the right math on play markup.
More of that in [docs/03-interpreting-gutenberg.md](docs/03-interpreting-gutenberg.md).

## Worked example (original text)

[examples/tiny-corpus/](examples/tiny-corpus/) is four short
paragraphs I wrote for this repo (cat, bread, telescope, garden).
No Gutenberg. You can count the tokens and reproduce every score.

```bash
python3 examples/tiny-corpus/run_tfidf.py --check
```

Identity the checker asserts:

```text
tf("moth", cats.txt) = 4/36 = 0.111111
idf("moth")          = ln(4/1) = 1.386294
tfidf                = 0.154033
```

`the` has a higher TF in that file and TF-IDF 0, because it appears
in all four notes.

## Docs

1. [What TF-IDF is](docs/01-what-is-tf-idf.md)
2. [Pipeline](docs/02-pipeline.md)
3. [Interpreting the Gutenberg results](docs/03-interpreting-gutenberg.md)
4. [Design notes](docs/04-design-notes.md)

## License-ish

The Perl and the write-ups are personal. The texts under
`gutenberg/` are public-domain Project Gutenberg editions, kept
here so the snapshot stays reproducible without a network fetch.
