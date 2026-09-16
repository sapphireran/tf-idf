# TF-IDF as implemented here

This page is the math that `tf-idf-values.pl` and `tf*idf-product.pl` compute. A three-document numerical example with the same formulas is in [../examples/tiny-corpus/walkthrough.md](../examples/tiny-corpus/walkthrough.md).

## Documents and terms

A **document** is one file. In the main experiment that means one Gutenberg text (`carroll-alice.txt`, `shakespeare-hamlet.txt`, …). In the toy example it means one file under `examples/tiny-corpus/docs/`.

A **term** is a token after [tokenization](tokenization.md): lowercase, alphanumeric, no stemming.

`N` is the number of documents in the collection. For the checked-in Gutenberg tables, `N = 18`.

## Term frequency (TF)

For every document `d` the script counts tokens, then writes a length-normalized frequency:

```
tf(t, d) = count(t, d) / tokens(d)
```

`tokens(d)` includes every kept token, so repeated words inflate the denominator. A word that appears twice in a 6-token document has `tf = 2/6 ≈ 0.333`.

This is **not** log-scaled TF (`1 + ln(count)`), **not** boolean TF, and **not** the raw count. The choice matters: *Moby-Dick* is an order of magnitude longer than *Alice*, so raw counts would not be comparable across `output/tf/*.txt`.

After a full run you will find one TSV per book in `output/tf/`, sorted by term (not by score).

### What TF alone looks like

The most frequent tokens in `carroll-alice.txt` are function words:

| term | tf |
| --- | --- |
| the | 0.06130 |
| and | 0.03176 |
| to | 0.02713 |
| a | 0.02359 |
| she | 0.02021 |
| alice | 0.01449 |

`alice` is already visible, but it is still below `the` / `and` / `to`. That is the problem IDF is for.

## Document frequency (DF)

```
df(t) = number of documents in which t occurs at least once
```

The Perl script stores this as a hash-of-hashes (`$df{$word}{$filename} = 1`) so each book contributes at most 1, regardless of how often the word repeats inside that book.

`output/df.txt` lists the term, the DF integer, and the file names. A word with `df = 18` is in every Gutenberg file in this collection. A word with `df = 1` is unique to one book.

## Inverse document frequency (IDF)

```
idf(t) = ln( N / df(t) )
```

`ln` is the natural logarithm. In Perl that is `log($n / $df)`. In Python it is `math.log(n / df)`.

Consequences of this exact formula:

| situation | idf |
| --- | --- |
| term in 1 of 18 books | `ln(18/1) ≈ 2.89037` |
| term in 7 of 18 books | `ln(18/7) ≈ 0.94446` |
| term in all 18 books | `ln(18/18) = 0` |

Those three values appear in the committed `output/idf.txt` (`00` at 2.890…, `1` at 0.944…, and everyday words such as `a` / `the` at 0).

There is **no** add-one smoothing and **no** `+ 1` shift. Many production IR systems use

```
idf_smooth(t) = ln( (N + 1) / (df(t) + 1) ) + 1
```

so that collection-wide words still get a small positive weight. This repo does not. A stopword that appears in every file is exactly zeroed out.

IDF is a property of the **collection**, not of a single book. The same `idf(alice)` multiplies every document's TF for `alice`. `alice` is not unique to Carroll: `output/df.txt` lists it in *Alice*, *The Man Who Was Thursday*, and *The Parent's Assistant*, so `df = 3` and `idf = ln(18/3) ≈ 1.79176`. It still wins Alice's ranking because its TF in that book is high, not because its DF is 1.

## TF-IDF product

```
tfidf(t, d) = tf(t, d) * idf(t)
```

`tf*idf-product.pl` reads `output/idf.txt` once, then for each `output/tf/<book>.txt` writes `output/tfidf/<book>.txt`.

For Alice, the same terms as above become:

| term | tf | idf (qualitative) | tfidf |
| --- | --- | --- | --- |
| the | 0.0613 | 0 (all 18 books) | 0 |
| and | 0.0318 | 0 | 0 |
| alice | 0.01449 | `ln(18/3) ≈ 1.792` (3 books) | 0.02596 |
| gryphon | small | `ln(18/2)` (Alice + *Paradise Lost*) | 0.00455 |

Ranking `output/tfidf/carroll-alice.txt` by the second column, not by the word, is how you get a character list instead of a stopword list. [interpreting-results.md](interpreting-results.md) has those rankings for several books.

## Why length-normalized TF × raw IDF is a reasonable teaching default

- **TF / tokens(d)** makes a 26k-token Alice comparable to a 212k-token Moby-Dick.
- **ln(N / df)** is the formula most tutorials write on the whiteboard.
- **The product** is one multiplication per term, which is what the second Perl script exists to show.

What this default does *not* do:

- It does not L2-normalize the TF-IDF vector, so you should not treat two books' scores as cosine-ready without another pass.
- It does not down-weight speaker abbreviations (`ham`, `macb`, `bru`) that happen to be rare across the collection. Those become "distinctive" for the wrong reason. See [known-quirks.md](known-quirks.md).
- It does not merge `have` / `haue` / `hath`. Early modern spelling therefore ranks high in the Shakespeare and Milton files.

## Variants you might meet elsewhere

Keep these distinct from this repo when you read other notes:

| name | typical formula | used here? |
| --- | --- | --- |
| raw TF | `count(t, d)` | no (we divide by length) |
| log TF | `1 + ln(count)` if count > 0 | no |
| boolean TF | 1 if present | no |
| raw IDF | `ln(N / df)` | **yes** |
| IDF + 1 | `ln(N / df) + 1` | no |
| smooth IDF | `ln((N+1)/(df+1))+1` | no |
| BM25 | saturated TF, length prior, tuned k1/b | no |

If you reimplement this project in another language and your IDF values for hapax terms are `3.890` instead of `2.890`, you added the `+ 1` shift.

## A compact derivation for the toy corpus

Three documents, six tokens each:

```
cats.txt:  the cat sat on the mat
dogs.txt:  the dog sat on the log
birds.txt: a bird sat on the nest
```

`N = 3`. Shared words `{the, sat, on}` have `df = 3` and `idf = 0`. Each distinctive noun (`cat`, `dog`, `bird`, …) has `df = 1` and `idf = ln(3) ≈ 1.098612`.

In `cats.txt`, `cat` occurs once, so

```
tf(cat, cats)    = 1/6 ≈ 0.166667
tfidf(cat, cats) = (1/6) * ln(3) ≈ 0.183102
```

`the` occurs twice:

```
tf(the, cats)    = 2/6 ≈ 0.333333
tfidf(the, cats) = (2/6) * ln(1) = 0
```

Every intermediate table for this example is checked in under `examples/tiny-corpus/expected/`.

## Numerical notes

- Perl and Python both use IEEE doubles. Printed values in `output/` are Perl's default stringification, which is why you see `3.76279349789284e-05` rather than a fixed number of decimals.
- `ln(18/1)` in the committed `idf.txt` is `2.89037175789616`.
- Division is ordinary floating-point division. There is no rounding step before the TF-IDF multiply.

If you need bit-identical output, run the Perl scripts. If you need readable arithmetic, use the tiny corpus and `examples/python/tfidf_example.py`.
