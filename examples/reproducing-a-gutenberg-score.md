# Reproducing one Gutenberg TF-IDF score

The checked-in tables are already the product `tf * idf`. This page multiplies
two of those files by hand so you can see that the third file is not doing
anything mysterious.

Formulas again:

```
tf(t, d)  = count(t, d) / tokens(d)     # output/tf/<doc>
idf(t)    = ln(18 / df(t))              # output/idf.txt
tfidf(t,d)= tf(t, d) * idf(t)           # output/tfidf/<doc>
```

## 1. `emma` in *Emma*

```bash
awk -F'\t' '$1=="emma" {print $2}' output/tf/austen-emma.txt
awk -F'\t' '$1=="emma" {print $2}' output/idf.txt
awk -F'\t' '$1=="emma" {print $2}' output/tfidf/austen-emma.txt
```

| Piece | Value in this checkout |
| --- | --- |
| `tf(emma, Emma)` | `0.00474787578393688` |
| `df(emma)` | `2` (*Emma* and a mention in *Persuasion*) |
| `idf(emma)` | `ln(18/2) = 2.19722457733622` |
| product | `0.00474787578393688 × 2.19722457733622 = 0.010432149362605586` |
| stored `output/tfidf/...` | `0.0104321493626056` |

The last-digit difference is ordinary float-to-text rounding.

`0.00475` TF means a bit under one token in two hundred is the string `emma`.
In a ~158k-word file that is hundreds of mentions — enough to beat every
other name even after the `df = 2` tax.

## 2. `harriet` in *Emma*

| Piece | Value |
| --- | --- |
| `tf` | `0.00246560793040664` |
| `df` | `1` |
| `idf` | `ln(18) = 2.89037175789616` |
| product | `0.00712652352809215` |

Harriet is said about half as often as Emma (`0.00247 / 0.00475 ≈ 0.52`) but
her IDF is larger (`2.890 / 2.197 ≈ 1.32`). `0.52 × 1.32 ≈ 0.68`, and
`0.00713 / 0.01043 ≈ 0.68`. The ranking gap is almost entirely TF; IDF only
narrows it.

## 3. `the` in *Emma*

| Piece | Value |
| --- | --- |
| `tf` | `0.0325333805381347` (~1 token in 31) |
| `df` | `18` |
| `idf` | `ln(1) = 0` |
| product | `0` |

Largest TF in the file, exact zero TF-IDF. If you ever see a nonzero `the`
in these tables, `N` or `df` has changed.

## 4. `whale` in *Moby-Dick*

```bash
awk -F'\t' '$1=="whale" {print $2}' output/tf/melville-moby_dick.txt
awk -F'\t' '$1=="whale" {print $2}' output/idf.txt
awk -F'\t' '$1=="whale" {print $2}' output/tfidf/melville-moby_dick.txt
```

| Piece | Value |
| --- | --- |
| `tf` | `0.0044997028498118` |
| `df` | `6` |
| `idf` | `ln(18/6) = 1.09861228866811` |
| product | `0.00494342884615816` |

Compare `ahab` in the same file: smaller TF, `df = 2`, idf `2.197`, product
`0.00432`. Same pattern as Emma vs Harriet, with the animal in Emma’s role
and the captain in Harriet’s.

## 5. The tiny-corpus twin

You do not need the Gutenberg files to practice the same multiplication:

```
tf(orchard, apple-orchard) = 2/20 = 0.1
idf(orchard)               = ln(4/1) = 1.38629436112
tfidf                      = 0.13862943611
```

`python3 examples/tiny-corpus/compute_tfidf.py --verify` asserts that identity.

## 6. When the identity will fail

- Regenerating IDF with `$#files` instead of `N = 18`
- Editing one TSV and not the others
- Parsing `thatyou`’s trailing `y` as part of the number and aborting
- Sorting the TF-IDF file as strings and thinking the top row is the top term

If you want a fresh product without touching Perl, multiply in Python:

```python
tf = 0.00474787578393688
idf = 2.19722457733622
print(tf * idf)
```
