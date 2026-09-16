# 03 — The 2012 Perl specimen

The two scripts at the repository root are the reason this notebook
has a shelf. I am reading them as a lab specimen, not rewriting them
in place.

## The pipeline

```
gutenberg/*.txt
        │
        ▼
 tf-idf-values.pl
        │
        ├── output/tf/<file>     term → f / word_count
        ├── output/df.txt        term → df, file names
        └── output/idf.txt       term → log(N / df)
                │
                ▼
     tf*idf-product.pl
                │
                └── output/tfidf/<file>   term → tf * idf
```

`tf*idf-product.pl` needs `Text::CSV_XS` only because it used a TSV
parser to read two-column text. The Python lab does not take that
dependency.

## Tokenization, line by line

For each line, `tf-idf-values.pl` does:

1. `chomp` — drop the newline.
2. Collapse horizontal/vertical whitespace to a single space.
3. `tr/[A-Z]/[a-z]/` — lowercase. The brackets are *inside* the
   transliteration sets, so `[` maps to `[` and `]` to `]`. Accidental,
   harmless for case folding.
4. Strip every character that is not alphanumeric or whitespace.
5. `split(/ +/, ...)` — split on runs of spaces.
6. Increment `word_count` for **every** piece, including empty
   strings.
7. Keep the piece in `%tf` and `%df` only when it is not `""`.

Consequences I have actually seen in `output/`:

- Apostrophes vanish, so `don't` becomes `dont` and `I'll` becomes
  `ill`. Those are different mistakes: one is a plausible collapsed
  form, the other collides with a real word.
- Hyphenated compounds become smashed (`rabbit-hole` → `rabbithole`)
  or, if the hyphen was surrounded by spaces, two tokens.
- Speech prefixes in the Shakespeare files lose their punctuation and
  become tokens such as `1murth` / `2murth` in the Macbeth TF-IDF
  table. Those are leftover stage-direction crumbs, not vocabulary.
- Title-line years (`1865`, `1603`) survive and often pick up the
  maximum IDF because they occur in one file.

## The `N` story

The script sets

```perl
my $n = $#files;
```

after `readdir`. In Perl, `$#files` is the **last index**, not the
count. `readdir` also yields `.` and `..` (and, on some machines,
`.DS_Store`). The 2012-09-10 commit message is "Bugfix: correcting
idf values in calculating number of files" and it rewrites every
`output/tfidf/*` plus `output/idf.txt` without touching the `.pl`
files. The numbers in those tables match

\[
\log(18 / n_t)
\]

exactly (`log(18) ≈ 2.89037175789616` for hapax terms). So the
checked-in tables were produced with \(N = 18\), the number of real
texts, while the script as committed still says `$#files`.

I am not "fixing" the Perl. The Python lab takes an explicit
`N = number of documents actually read` and writes that choice down.

## Length denominator

Normalized TF is `count / word_count`, and `word_count` includes the
empty split pieces. On clean prose the fraction of empties is small.
On lines that are only punctuation (common in verse and plays) the
denominator inflates and every TF on that file shrinks a little. The
tiny-corpus tests use a tokenizer that does **not** count empties,
and [07](07-tokenization-and-stopwords.md) shows how to ask the lab
for the legacy denominator.

## The product script

`tf*idf-product.pl` multiplies the two columns and writes a new
sorted table. It does not rank queries. If a term is missing from
`output/idf.txt` the Perl hash lookup yields `undef`, which numifies
to `0` in the multiplication. Missing IDF therefore becomes a silent
zero rather than an error.

## What I keep from the specimen

- Normalized TF × \(\log(N / n_t)\) is a coherent default.
- Writing intermediate tables (`tf/`, `df`, `idf`) is the right
  teaching move. I kept that habit in `python3 -m tfidf explain`.
- Off-by-one on `N` and empty-token counting are the two bugs I want
  every later experiment to name out loud.
