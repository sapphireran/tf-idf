# Why document units matter more than the formula

Classic TF-IDF is a short recipe:

```
tf(t, d)  = count(t, d) / words(d)
idf(t)    = ln(N / df(t))
tfidf     = tf * idf
```

Almost every tutorial stops at the recipe. The interesting argument is
hiding in `N` and `df`. Both numbers are not properties of language. They
are properties of **how you chopped the shelf**.

## The same word, three filings

Take `hatter` in *Alice's Adventures in Wonderland*.

| Filing | What `hatter` is |
| --- | --- |
| File-level (2012 toy) | A term that lives in one of 18 Gutenberg files. IDF is `ln(18/1)` if no other file says "hatter". The weight is diluted across the whole novel. |
| Chapter-level | A term that lives mainly in Chapter VII and the trial. IDF is `ln(12/df_chapters)`. The tea-party chapter suddenly looks like a tea-party chapter. |
| Passage-level | A term that lives in a few 80-token windows. Retrieval can point at the song, not the book. |

None of those filings change the formula. They change the *question*.
File-level TF-IDF answers "which book on this shelf is about this
vocabulary?" Chapter-level answers "where in the book?" Speaker-level
answers "who talks like this?"

## A small numeric picture

Suppose a toy shelf of three notes:

- A: `cat cat cat milk`
- B: `dog dog milk`
- C: `bread bread`

Then `milk` has `df = 2`, `idf = ln(3/2) ≈ 0.405`. In A its TF-IDF is
`(1/4) * 0.405 ≈ 0.101`. `cat` has `df = 1`, so `(3/4) * ln(3) ≈ 0.824`.
The math is saying: *cat* is what A is about, *milk* is shared furniture.

Now staple A and B into one file called `pets`. `cat` still has `df = 1`
if C is the only other file, but its TF is now 3/7 instead of 3/4, and you
can no longer ask "is this the cat note or the dog note?" You fused the
units and the question died.

That is what the 2012 Gutenberg run does to the King James text, to
*Paradise Lost*, and to *Moby-Dick*. It is a legitimate first pass. It is
a blunt instrument for reading.

## What this kit changes

| Command | Unit |
| --- | --- |
| `python3 -m shelf_units rank … --units gutenberg` | One file = one document (the 2012 grain) |
| `python3 -m shelf_units bible` | One titled KJV book = one document |
| `python3 -m shelf_units chapters carroll-alice` | One chapter = one document |
| `python3 -m shelf_units voices shakespeare-macbeth` | One speaking voice = one document |
| `python3 -m shelf_units commonplace` | One personal note = one document |
| `python3 -m shelf_units passages …` | One token window = one document |

The rest of these notes are just that table, walked slowly, with numbers
taken from this checkout.
