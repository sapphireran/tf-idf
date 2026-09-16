# Quirks and limitations

The 2012 scripts are short on purpose. The surprises below are the
useful part of keeping them around.

## 1. `$n = $#files` is not a document count

Pass 1 ends with:

```perl
my $n = $#files;
my $idf_val = log($n/($#vals+1));
```

`readdir` on a Unix directory includes `.` and `..`. For 18 texts that
is typically 20 names, and `$#files` (the last index) is 19. IDF would
then be `ln(19/df)`.

A word present in all 18 files would get `ln(19/18) ≈ 0.054`, not 0.

The committed `output/idf.txt` does **not** look like that. `the` and
`a` have IDF 0, `whale` has `ln(18/6)`, `buster` has `ln(18)`. The
snapshot was produced with **N = 18**.

The teaching code refuses to copy the `$#files` shortcut:

```python
n_docs = len(tf_tables)
idf[term] = math.log(n_docs / df[term])
```

If you rerun the original Perl as-is, do not expect bit-identical IDF
tables unless you also change how `N` is measured. Counting the files
you actually tokenized is the version that matches the blog-era dump.

## 2. `tr/[A-Z]/[a-z]/` is not a regex

In Perl, `tr///` does not honor character classes the way `s///` does.
The search list `[A-Z]` is the characters `[`, `A` through `Z`, and
`]`. The replacement list `[a-z]` is `[`, `a` through `z`, and `]`.
Brackets map to themselves; letters map to lowercase. It works, but it
works by coincidence.

The Python toy just calls `str.lower()`. The Perl toy uses
`tr/A-Z/a-z/`, which is the spelling that means what it looks like.

## 3. Apostrophes and hyphens disappear

The strip step is "keep letters, digits, and whitespace." So:

| original | tokens |
| --- | --- |
| `alice's` | `alices` |
| `don't` | `dont` |
| `o'er` | `oer` |
| `First Folio` `haue` | `haue` (already one token) |
| `Moby-Dick` | `moby` `dick` if hyphenated that way in running text |

Blake's `oer` ranking is this rule, not a mysterious dialect.

## 4. Digits stay

Verse numbers, chapter numbers, and stray catalog ids become
vocabulary. `output/idf.txt` begins with tokens like `00`, `00021053`,
`1`, `1001`. Most have maximum IDF because they appear in one file.
They almost never win a **document** ranking, because their TF is tiny
compared with `whale` or `emma`. They still inflate the vocabulary
into the tens of thousands.

## 5. No stopword list, on purpose

The tiny corpus makes this obvious. `garden.txt` ranks `at` second
because `at` occurs twice in that vignette and in none of the others.
`kitchen.txt` ranks `and` next to `salt` for the same reason.

On Gutenberg, the same effect promotes:

- `mr` / `mrs` in Austen (common in those novels, rarer in Shakespeare
  verse)
- `unto` / `thou` / `hath` in the Bible and Milton
- `o` in Whitman
- `ebook` in *The Ball and the Cross*

A stopword list would hide some of those. It would also hide the fact
that IDF is only as smart as the collection. This toy leaves the
awkward terms visible.

## 6. Plays are not prose

The Macbeth file looks like:

```
  Macb. So foule and faire a day I haue not seene
```

After tokenization, `macb` is a high-frequency term unique to that
file. TF-IDF concludes, correctly, that `macb` is an excellent feature
for identifying the Macbeth document. It does not conclude anything
about ambition or Birnam Wood.

`--min-length 4` on the ranking helper is a crude scalpel, not a
parser.

## 7. Stemming is absent

`whale` and `whales`, `anarchist` and `anarchists`, `turnbull` and
`turnbulls` are separate terms. They often sit next to each other in
the top 10, which is a hint that a stemmer would concentrate the mass.

## 8. Filename globbing

`tf*idf-product.pl` will expand to something unintended if you type:

```bash
perl tf*idf-product.pl
```

in a directory that also matches other `tf*` files. Quote the name.

## 9. `Text::CSV_XS` for TSV

Pass 2 depends on a CPAN module to split on tabs. That is optional
complexity; `split(/\t/, $line, 2)` is enough for this data. The
example Perl script does that and enables `use warnings`.

## 10. The dump is a snapshot

Rerunning pass 1 and pass 2 rewrites large files and can change
floating-point formatting. The docs and ranking helper treat
`output/` as frozen teaching data. The tiny corpus is the part that is
meant to be regenerated freely.

## What a next personal experiment could change

None of these are requested by this docs pass; they are the obvious
knobs if you keep playing with the toy:

- count `N` from tokenized files
- optional stopword file
- drop tokens of length 1 and pure-digit tokens
- write top-k files next to the alphabetical dumps
- cosine-normalize each document vector and add a "find similar book"
  script

The five-vignette example is the place to try those, not the 18-book
dump.
