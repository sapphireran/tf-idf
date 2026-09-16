# Quirks of this implementation, and common variants

The 2012 scripts are short on purpose. This page records the sharp
edges so the examples can show both "what the repo actually did" and
"what you might do next in a personal notebook."

## \(N\) is not `readdir` length

`tf-idf-values.pl` sets

```perl
my $n = $#files;
```

after `readdir("gutenberg")`. On a typical checkout that array is:

```
.   ..   .DS_Store   <18 *.txt files>
```

so `$#files` is 20, and a naïve rerun would use \(N = 20\). The original
committed IDF table used \(N = 20\) (\(\ln 20 \approx 2.99573227355399\)
for terms with \(\mathrm{df} = 1\)). Commit `b50ebb9` ("Bugfix:
correcting idf values in calculating number of files") rewrote
`output/idf.txt` and every `output/tfidf/*` file to \(N = 18\)
(\(\ln 18 \approx 2.89037175789616\)) and **did not change the script**.

So:

- The **checked-in results** are the pedagogically correct count: 18
  books.
- The **checked-in script** still does not compute that count.

`examples/tfidf_lib.py` never uses directory-entry indexes. It sets
\(N\) to the number of documents it actually tokenized, or to an
explicit override. That is the definition used in
[tf-idf-math.md](tf-idf-math.md).

If you regenerate Gutenberg IDF with \(N = 20\), every score changes and
terms that appear in all 18 books get a small positive IDF
(\(\ln(20/18) \approx 0.105\)) instead of zero. Rankings of rare names
barely move; rankings of `the` do.

## Tokenization is ASCII-punctuation deletion

Apostrophes, diacritics, and hyphens vanish. That produces a usefully
ugly vocabulary:

| Surface form | Token | Consequence |
| --- | --- | --- |
| `Alice's` | `alices` | Possessives do not join `alice`. |
| `don't` | `dont` | Negations are opaque. |
| `o'er` | `oer` | Shows up in Blake's top terms. |
| `Ham.` | `ham` | Speaker tags become "words." |
| `have` in Folio | `haue` | `u`/`v` spelling splits the mass of *have*. |

A modern spaCy / regex `\b\w+\b` tokenizer would still not fix Folio
spelling. Stemming would merge `whale`/`whales` and would also merge
things you may not want (`israel` / `israeli` if both appeared).

## TF is raw proportion, not log TF

Many IR systems use \(1 + \log n_{t,d}\) (or BM25's saturated TF) so
the 400th occurrence of `whale` adds almost nothing. Here the 400th
occurrence adds as much TF as the first. That is why *Moby-Dick* can
put `whale` at the top even though the book is long: the raw count is
enormous. It is also why a repeated speaker tag wins a play.

`examples/tfidf_lib.py` implements an optional `log_tf` mode:

\[
\mathrm{tf}_{\log}(t, d) = \begin{cases}
0 & n_{t,d} = 0 \\
1 + \ln n_{t,d} & n_{t,d} \ge 1
\end{cases}
\]

This is **not** what the Perl writes. The flag exists so the
walkthroughs can show the difference on the three-document toy.

## IDF is unsmoothed natural log

Standard variants, all supported as named modes in the example library:

| Name | Formula | Why people use it |
| --- | --- | --- |
| `raw` (this repo) | \(\ln(N / \mathrm{df})\) | Matches the Perl. Hits exact 0 for collection-wide terms. Undefined if \(\mathrm{df} = 0\). |
| `smooth` | \(\ln((N + 1) / (\mathrm{df} + 1)) + 1\) | scikit-learn's default-ish shape. Never zero, defined for unseen terms if you keep the \(+1\). |
| `prob` | \(\ln((N - \mathrm{df}) / \mathrm{df})\) | Robertson–Sparck Jones flavor. Negative for terms in more than half the docs. |

Smoothed IDF is the right illustration of "stopwords need not be
exactly zero." On the three-document toy, `the` gets a small positive
weight instead of disappearing.

## No length normalization beyond TF

TF already divides by \(|d|\). There is no cosine-length step at
**index** time. If you want to compare documents to each other, apply
cosine at query time (`examples/cosine_similarity.py`). If you want
BM25-style "long documents are not penalized as hard," that is a
different formula and is not implemented here.

## Document frequency is binary per file

A word mentioned 500 times in *Moby-Dick* and once in the Bible has
\(\mathrm{df} = 2\), same as a word mentioned once in each. IDF does
not care about *how often* the other document used it. That is standard.

## The product script depends on CPAN

`tf*idf-product.pl` is the only file that needs `Text::CSV_XS`. The
split is ordinary TSV; the example Python reads the same files with
`str.split("\t")`. You do not need Perl to study the committed output.

## Regenerating `output/` is a large diff

`output/idf.txt` is 57k lines; the TF-IDF files together are a few
megabytes. The 2012 bugfix is a 389k-line whitespace-and-number churn.
Do not regenerate those files in this personal docs branch unless the
goal is a new experiment. Point new writeups at `examples/mini_corpus/`
or at scripts that *read* the existing tables.

## Checklist for a personal extension

If you fork this for another hobby corpus:

1. Count \(N\) as "files I tokenized," never `$#readdir`.
2. Strip headers and license footers before TF.
3. Decide on apostrophes (`alice's` vs `alice` + `s`).
4. Keep a stopword list if you care about `unto` / `thee`.
5. Rank with a script; do not eyeball alphabetical dumps.
6. Compare documents with cosine, not by subtracting top scores.

The example programs follow (1), (5), and (6). They leave (2)–(4) off
so they stay comparable to the Perl.
