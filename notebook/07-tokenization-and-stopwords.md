# 07 — Tokenization and stopwords

The weighting formulas are the clean part. The messy part is deciding
what a term is.

## Two tokenizers in the lab

**`simple` (default).** Lowercase, keep runs of `[a-z0-9]+`, drop
everything else. `don't` → `don` + `t`. `rabbit-hole` → `rabbit` +
`hole`. Years in title lines stay (`1865`). This is the tokenizer
the tests and the worked example use.

**`perl_legacy`.** Recreates the 2012 steps, including counting empty
split pieces in the length denominator. `don't` → `dont`.
`rabbit-hole` → `rabbithole`. Useful when I want to line a number up
against `output/tf/`.

```bash
python3 -m tfidf explain rabbithole --doc gutenberg/carroll-alice.txt --tokenizer perl_legacy
python3 -m tfidf explain rabbit --doc gutenberg/carroll-alice.txt --tokenizer simple
```

Those two commands are about different terms. That is the lesson.

## Stopwords

IDF already sends collection-wide words toward zero under `classic`.
A stoplist is still useful when I want to look at a top-terms list
without staring at `said`, `mr`, and `the` under a smoothed IDF.

The lab ships a short English list in `tfidf/stopwords.py`. It is a
convenience, not a theory of function words. Enable it with
`--stopwords`.

I do **not** apply the stoplist when I am trying to reproduce the
2012 tables. Those tables kept `the` and then multiplied it by IDF
0.

## Shakespeare crumbs

Opening `output/tfidf/shakespeare-macbeth.txt` shows terms like
`1murth` and `2murth`. Those are Perl-tokenizer leftovers (digits
glued to stripped stage-direction text). The `simple` tokenizer
splits digit runs from letter runs, so those exact strings do not
appear in `python3 -m tfidf top --doc gutenberg/shakespeare-macbeth.txt`.
What *does* appear is the same kind of junk in a different font:
speech prefixes (`macb`, `macd`) and Early Modern spellings
(`haue`, `vpon`) with high IDF because Austen does not share them.

`--alpha-only` drops tokens that contain a digit. It does not drop
`macb`. A modern English stoplist does not drop `haue`.

## Apostrophes, again

| Surface | `simple` | `perl_legacy` |
| --- | --- | --- |
| `I'll` | `i`, `ll` | `ill` |
| `don't` | `don`, `t` | `dont` |
| `o'clock` | `o`, `clock` | `oclock` |
| `Alice's` | `alice`, `s` | `alices` |

None of these is "correct." They are different losses. If I ever add
a third tokenizer it will be "Unicode word letters plus internal
apostrophes," and it will get its own note rather than silently
replacing these two.

## Why `the` scores 0 in the 2012 TF-IDF files

`the` appears in all eighteen Gutenberg documents. Classic IDF is
\(\log(18/18) = 0\). The TF file still has a large number. The
product is zero. That is working as designed, and it is why a
top-terms listing over `output/tfidf/` is already a de-facto
stopword filter for collection-wide function words.
