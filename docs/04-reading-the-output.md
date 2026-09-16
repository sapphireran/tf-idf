# Reading the committed output

Every file under `output/` is a tab-separated table from the 2012 run. None of them are ranked. Sort them yourself, or use `examples/python/rank_terms.py`.

## `output/tf/<book>.txt`

```
token<TAB>tf
```

- One row per distinct token in that book
- `tf` is `count / word_count` for that book
- Sorted by token, ASCII order
- Tokens that do not occur are omitted (sparse)

Example, Alice:

```
1865	3.76279349789284e-05
a	0.0235927152317881
abide	3.76279349789284e-05
```

`1865` is the year in the Gutenberg-style header. `a` is a function word with high `tf` and, later, zero `idf`.

## `output/df.txt`

```
word<TAB>#docs it exists in<TAB>doc names
```

The first line is a header. Each later line is:

```
alice	3	carroll-alice.txt, chesterton-brown.txt, austen-emma.txt,
```

(The actual posting order follows Perl hash key order from 2012, not alphabetical file order.) Names are comma-space separated and the list ends with a trailing comma-space.

`#docs` is `df(t)`. It should equal the number of filenames in the third column.

## `output/idf.txt`

```
token<TAB>idf
```

No header. `idf = ln(18 / df(t))` for every well-formed row.

One row in the frozen snapshot is corrupt:

```
thatyou	2.89037175789616y
```

The leading float is the correct `ln(18/1)` value; a trailing `y` was written into the cell. The Python readers strip trailing non-numeric junk and log a warning. See [05-quirks-and-design-choices.md](05-quirks-and-design-choices.md).

## `output/tfidf/<book>.txt`

```
token<TAB>tf*idf
```

Same token order as the matching `tf` file. A token present in `tf` but missing from `idf` would become a CSV parse issue in the Perl product script; the committed snapshot does not have that hole except for the `thatyou` cell, which `Text::CSV_XS` still reads as a field.

Zeros are stored as `0`, not omitted. Corpus-wide tokens therefore still appear in every `tfidf` file with weight 0.

## `output/df-sorted.txt`

A one-line leftover from the original snapshot. It is not used by either Perl script.

## How to rank a book

Alphabetical `tfidf` files hide the interesting words. To see Alice the way the worked note presents her:

```bash
python3 examples/python/rank_terms.py \
  --tfidf-dir output/tfidf \
  --document carroll-alice.txt \
  --top 15
```

Or with only standard Unix tools:

```bash
sort -t$'\t' -k2,2nr output/tfidf/carroll-alice.txt | head
```

## How to ask "where does this token live?"

```bash
python3 examples/python/inspect_committed.py --token alice
```

That prints `df`, `idf`, the posting list from `df.txt`, and the token's `tf` / `tfidf` in each book that contains it.

## Do not treat `output/` as regenerated

The tables are a historical artifact. Re-running `tf-idf-values.pl` on this tree can change `N` (see the pipeline note). Re-running the Python pipeline into a fresh directory is the supported way to recompute. Leave `output/` alone unless you are deliberately replacing the snapshot.
