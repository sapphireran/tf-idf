# How these weights read

The 2012 Perl does one thing and stops. It does not rank queries, it
does not cosine-normalize a document, and it does not drop stopwords
by list. It writes three families of TSV files. This note is the
minimum you need in order to read those files as a person, not as a
search engine.

## The product

For every surviving token *t* in book *d*:

```
tf(t, d) = raw count of t in d / token count of d
idf(t)   = ln(N / df(t))
tfidf    = tf * idf
```

`N` on the snapshot is **18**. `df(t)` is the number of book files
that contain *t* at least once after the tokenizer. The log is the
natural log (Perl's `log`). There is no `+1` in either the numerator
or the denominator.

Consequences you will keep bumping into:

1. **A word in every book has weight zero.** `the`, `a`, and `and`
   have `idf = ln(18/18) = 0`. Their rows still exist in
   `output/tfidf/carroll-alice.txt`; the second column is `0`.
2. **A word in one book has `idf = ln(18) ≈ 2.89037`.** That is the
   ceiling. `buster`, `macbeth`, `ebook`, and `gryphon` all sit on
   it. The remaining variation is pure term frequency.
3. **A word in two books has `idf = ln(9) ≈ 2.19722`.** `emma` is
   here. The name is almost private to *Emma*, but not quite.
4. **Length is in the denominator of TF.** Repeating a rare name in
   a 16k-word children's book outruns mentioning `whale` hundreds of
   times in a 212k-word novel. The next note is entirely about this.

## What the tokenizer keeps

`tf-idf-values.pl` lowercases, squeezes horizontal/vertical space,
and then strips every character that is not ASCII letter, digit, or
space. Apostrophes vanish, so `Alice's` becomes `alices`. Folio
spellings stay (`haue`, `vpon`), because they are already letters.
Hyphenated compounds become smashed or split depending on whether
the hyphen was the only separator.

`split(/ +/)` on a line that starts with spaces produces empty
fields. The script skips `""` when incrementing TF/DF, but the empty
string still advances the per-file token counter. That slightly
deflates every TF in a file with indented verse or drama.

One snapshot scar is worth knowing about: `output/idf.txt` line
50450 is `thatyou` with a trailing `y` glued onto the float
(`2.89037175789616y`). A tokenizer smash (`that` + `you`) plus a
stray character. The companion loader skips rows that do not parse
as floats. Nothing in `output/tfidf/` depends on that one IDF line.

## How to read one row

From `output/tfidf/carroll-alice.txt`:

```
alice	0.025957...
gryphon	0.004547...
a	0
```

- `alice` is frequent in a short book and rare on the shelf
  (`df = 3`, `idf ≈ 1.792`). Frequency times rarity is the largest
  number in that file.
- `gryphon` is rarer (`df = 1`) but much less frequent, so it loses
  to the title character.
- `a` is common in Alice and common everywhere, so it is a zero.

The same pattern is why *Moby-Dick*'s top term is `whale` and not
`the`, and why the King James Bible's top term is `unto` rather than
`god` or `lord`. `unto` is both frequent in that file and uncommon
in the later prose.

## What cosine is doing in the companion

The Perl never builds a query vector. The companion scripts treat
each `output/tfidf/*.txt` file as a sparse vector and, when they
need a book-to-book or query-to-book number, take

```
cos(u, v) = (u · v) / (||u|| ||v||)
```

That is a reading tool, not a claim that the 2012 scripts ranked
anything. A query is a bag of already-lowercased tokens. Terms with
weight zero in a book do not help that book. Terms missing from a
book contribute nothing. A query of pure stopwords (`the and of`)
therefore scores every book at 0.0000.

## File formats

| File | Columns |
| --- | --- |
| `output/tf/<book>` | `term`, normalized TF |
| `output/idf.txt` | `term`, `ln(N/df)` |
| `output/df.txt` | `term`, document count, comma-separated filenames |
| `output/tfidf/<book>` | `term`, product |

Rows are sorted alphabetically by term, not by score. Use
`term_atlas.py` when you want the heavy end of a book.
