# Reading the checked-in tables

Everything under `output/` is tab-separated text. You can `grep`, `sort`,
or point the Python examples at a directory.

## `output/df.txt`

```
word 	 #docs it exists in 	 doc names
alice	3	chesterton-thursday.txt, carroll-alice.txt, edgeworth-parents.txt,
macbeth	1	shakespeare-macbeth.txt,
the	18	<every filename>,
```

Column 2 is `df`. Column 3 is an unordered, comma-spaced list of source
files; it is a debug aid, not an identifier. The header uses spaces around
the tabs, the data rows do not.

`output/df-sorted.txt` is the same information in a different order.

Useful checks:

```bash
# How rare is a word on the shelf?
grep -E '^(alice|whale|the)\t' output/df.txt

# Terms that appear in exactly one book
awk -F '\t' 'NR>1 && $2==1 {c++} END {print c}' output/df.txt
```

On the checked-in snapshot there are 57,368 data rows in `df.txt` and
57,367 rows in `idf.txt` (the header accounts for the extra DF line).

## `output/idf.txt`

```
alice	1.79175946922805
whale	1.09861228866811
the	0
macbeth	2.89037175789616
```

No header. Values are `ln(18 / df)`. Confirm a row with:

```bash
python3 -c "import math; print(math.log(18/3), math.log(18/6), math.log(18/1))"
```

which prints the `alice` / `whale` / `macbeth` IDFs above.

221 terms have IDF 0. Those are the words that occur in all 18 books.

## `output/tf/<book>.txt`

```
alice	0.015026...
the	0.02359...
```

Normalized frequency: count divided by that file's token count. Rows are
sorted alphabetically, not by score. A missing term means count 0; there
is no explicit zero row.

Because length includes stopwords, even a theme word is a few percent of
the stream. `alice` at ~1.5% is already a dominant name.

## `output/tfidf/<book>.txt`

```
alice	0.025956780390307
all	0
whale	<absent from Alice>
```

Same alphabetical order as the TF file. `all	0` is a real row: the term
occurred in Alice, but `IDF(all) = 0`. A term Alice never uses is simply
missing, which is different from a zero weight.

**Do not `sort -n` these files.** Many weights are in scientific notation
(`9.64e-05`). GNU `sort -n` reads that as `9.64`. Use general numeric
sort, or the ranker:

```bash
sort -t $'\t' -k2,2g -r output/tfidf/carroll-alice.txt | head
python3 examples/rank_terms.py carroll-alice --top 10
```

`sort -g` and `rank_terms.py` both put `alice` first. `sort -n` will
promote the `9e-05` rows and hide the real head of the list.

## Looking up one word across books

There is no wide matrix checked in. To see `whale` everywhere:

```bash
grep -H $'^whale\t' output/tfidf/*.txt
```

Or score a query, which sums several such rows:

```bash
python3 examples/query_documents.py whale ahab pequod
```

## Precision

The Perl scripts print default floating-point strings, not rounded
percentages. Comparing tables after a regenerate will show tiny drift if
`N` or the tokenizer changes, and large drift if `$#files` is not 18.
Keep the committed `output/` as the reference snapshot unless you intend
to replace it.
