# Tokenization and other quirks

The personal toy is small enough that its rough edges are visible in the
tables. This note records the ones that change how you read a ranking.

## The tokenizer

`tf-idf-values.pl` and `examples/tiny_tfidf.py` do the same four steps:

1. Lowercase with a transliteration (`A-Z` → `a-z`).
2. Squeeze any horizontal or vertical whitespace to a single space.
3. Delete every character that is not `[a-zA-Z0-9]` or a space.
4. Split on spaces and drop empty tokens.

There is no Unicode letter class, no apostrophe handling, and no hyphen
handling. Demo those cases with:

```bash
python3 examples/inspect_tokenize.py
python3 examples/inspect_tokenize.py "Alice's Adventures in Wonderland"
```

### Apostrophes vanish

`Alice's` becomes `alices`. `won't` becomes `wont`. `tis` survives if the
leading quote is stripped, but `'tis` becomes `tis`. Possessives and
negations therefore do not match the bare stem (`alice` ≠ `alices`).

### Hyphens fuse or split depending on spacing

`Moby-Dick` becomes `mobydick` (hyphen deleted, no space inserted).
`Moby Dick` becomes two tokens. The checked-in Melville file uses both
patterns, which is why `moby` and `dick` can appear without a
`moby-dick` term.

### Punctuation between letters fuses words

If two words are separated only by a character that step 3 deletes, they
become one token. That is where rows such as `aliceand`, `ahabtheres`,
`whalethe`, and `thetable` come from. They look like bugs in `df.txt`
and are just the tokenizer concatenating across a hyphen, em-dash, or
missing space in the Gutenberg transcription.

### Digits are tokens

Chapter numbers, years (`1865` in the Alice header), and verse numbers
in the KJV all enter the vocabulary. They usually have `df = 1` and a
tiny TF, so they rarely win a ranking, but they inflate the 57k vocab.

## Speaker tags outrank titles

The Shakespeare files keep abbreviated speech prefixes:

| File | Prefix token | Title token |
| --- | --- | --- |
| `shakespeare-hamlet.txt` | `ham` 0.014075 | `hamlet` 0.003582 |
| `shakespeare-macbeth.txt` | `macb` 0.021556 | `macbeth` 0.009755 |
| `shakespeare-caesar.txt` | `bru` 0.0208, `cassi` 0.0146, `caes` 0.0053 | `brutus` 0.0167, `caesar` 0.0073 |

`HAM.` → `ham`, `MACB.` → `macb`. A query for `hamlet` still finds the
right play because `hamlet` itself has weight there; it just is not the
heaviest token in the file. If you want "character names only," you
would have to strip prefixes before counting — this repo does not.

Early-modern spelling (`haue`, `selfe`, `loue`, `giue`, `vpon`) is the
same story: those strings are concentrated in the three play files, so
IDF treats them as distinctive even though they are ordinary words in
modern spelling.

## `N` in the Perl IDF line

```perl
opendir(DIR, "gutenberg");
my @files = readdir(DIR);
# ...
my $n = $#files;                    # last index, not count
my $idf_val = log($n / ($#vals+1));
```

`readdir` includes `.` and `..`. `$#files` is `scalar(@files) - 1`. The
loop already skips names that start with `.`, so the processed count and
`$n` are not defined the same way.

The committed `output/idf.txt` agrees with **processed `N = 18`**:

```
ln(18 / 1) = 2.89037175789616
ln(18 / 2) = 2.19722457733622
ln(18 / 3) = 1.79175946922805
```

If you re-run the script as-is, `$n` will follow however many directory
entries `readdir` returned, minus one. Adding `.DS_Store` or an extra
scratch file changes IDF for every term.

A definition that matches the committed tables:

```perl
my $n = 0;
$n++ for grep { $_ !~ /^\./ } @files;
my $idf_val = log($n / ($#vals + 1));
```

The Python toy already uses `N = len(docs)` after applying the same
hidden-file skip. It will not reproduce a regenerate that used `$#files`.

This repo leaves the original Perl line in place and treats `output/` as
a snapshot. The docs and examples assume `N = 18` for Gutenberg and
`N = 4` for `examples/tiny-corpus`.

## Zero weights versus missing weights

* **Zero TF-IDF, row present:** the term occurred in that document and
  in every document (`IDF = 0`). Example: `all` in Alice.
* **Row absent:** the term never occurred in that document. `whale` is
  absent from `output/tfidf/carroll-alice.txt`.

`query_documents.py` treats both as a 0 contribution. `rank_terms.py`
only sees present rows, so an IDF-0 term can still show up at the bottom
of a full listing.

## Files the pipeline should ignore

* Names starting with `.` in `gutenberg/` (skipped).
* `output/tf/.DS_Store` if present (binary; not a term table).
* `output/df-sorted.txt` (not rewritten by the Perl scripts).

## Practical advice when a term "is missing"

1. Run the string through `examples/inspect_tokenize.py`.
2. `grep` `output/df.txt` for fused leftovers (`alices`, `mobydick`).
3. Remember that query terms are not stemmed: `whales` ≠ `whale`.
4. Check `df`. A word that is in every book cannot rank anything.
