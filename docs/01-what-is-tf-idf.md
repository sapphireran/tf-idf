# What TF-IDF is

TF-IDF is a cheap way to ask: *which words make this document look
different from the rest of the folder?* It is not a language model
and it is not a search engine. It is a per-term score built from two
counts you can do on paper.

This repo uses the textbook product

```text
tfidf(term, doc) = tf(term, doc) * idf(term)
```

with **normalized term frequency** and **natural-log inverse document
frequency, no smoothing**. Those two choices match
`tf-idf-values.pl` and `tf*idf-product.pl`.

## Term frequency

Raw count is a poor score on its own. A 4 MB Bible will mention
"and" more times than a 38 KB Blake poem mentions "lamb". The Perl
script divides by the number of tokens in that file:

```text
tf(term, doc) = count(term, doc) / word_count(doc)
```

`word_count` is the number of split tokens, including empty ones
left behind by the tokenizer. Indexed terms are only the non-empty
tokens. On clean prose the two numbers are almost equal; on a file
full of punctuation-only lines they drift apart. Details are in
[04-design-notes.md](04-design-notes.md).

On the tiny corpus, `moth` occurs 4 times in a 36-token cat note:

```text
tf("moth", cats.txt) = 4 / 36 = 0.111111
```

`the` occurs 7 times in the same note:

```text
tf("the", cats.txt) = 7 / 36 = 0.194444
```

If you stopped here, `the` would win. That is why the second factor
exists.

## Document frequency and IDF

Document frequency is **how many files contain the term at least
once**, not how many times it occurs.

```text
df(term) = |{ doc : count(term, doc) > 0 }|
idf(term) = ln(N / df(term))
```

`N` is the corpus size. The tiny example uses `N = 4`. The
checked-in Gutenberg `output/` was computed with `N = 18`, one per
`.txt` file under `gutenberg/`.

Properties of this IDF, which is exactly `log($n/($#vals+1))` in
Perl (natural log):

| Situation | IDF |
| --- | --- |
| Term in one file | `ln(N)` — largest possible value |
| Term in every file | `ln(1) = 0` |
| Term in half the files | `ln(2) ≈ 0.693` |

There is no add-one (`ln(N / (df+1))`) and no smoothed variant
(`ln((N+1) / (df+1))`). A word that really does appear in every
document is assigned **exactly zero** and cannot contribute to any
TF-IDF vector.

On the Gutenberg run that is not hypothetical. `a` and `the` appear
in all 18 texts, so their IDF rows are `0`. 221 terms do that.
About 36,887 of the 57,368 distinct terms appear in only one file
and take `ln(18) ≈ 2.890`.

Worked Gutenberg values, copied from `output/idf.txt` and
`output/df.txt`:

| term | df | IDF | why |
| --- | ---: | ---: | --- |
| macbeth | 1 | 2.890372 | only the play |
| ahab | 2 | 2.197225 | Moby-Dick and the KJV (the biblical Ahab) |
| emma | 2 | 2.197225 | the novel and one other hit |
| alice | 3 | 1.791759 | Carroll, *Thursday*, Edgeworth |
| hatter | 3 | 1.791759 | Carroll plus two stray hits |
| whale | 6 | 1.098612 | Melville and five other books |
| innocence | 2 | 0.693147 | Blake plus one other |
| the | 18 | 0 | every file |

Alice the character is not unique to `carroll-alice.txt`. IDF still
helps because three documents out of eighteen is rare enough that
`ln(18/3) = ln(6) ≈ 1.79` leaves plenty of weight for a word that
occurs 385 times in that file.

## The product

From the checked-in Alice files:

```text
tf("alice", carroll-alice.txt)  = 0.0144867549668874
idf("alice")                    = 1.79175946922805
tfidf                           = 0.025956780390307
```

and

```text
tf("the", carroll-alice.txt)    = 0.0612959060806743
idf("the")                      = 0
tfidf                           = 0
```

`the` is about four times more common than `alice` inside the book
and disappears from the ranking. `alice` is the top term in
`output/tfidf/carroll-alice.txt`.

The same identity on the tiny corpus:

```text
tf("moth", cats.txt) = 0.111111
idf("moth")          = 1.386294
tfidf                = 0.154033
```

## What the score is for

TF-IDF as computed here is a **descriptive ranking**, not a
classifier.

- High inside one file: a word you could use as a label for that
  file relative to this folder.
- Zero: either the term never appears, or it appears so widely that
  this corpus refuses to treat it as news.
- Middle: a word that is somewhat common and somewhat shared
  (`whale` is the classic — it leads Moby-Dick even though six
  files mention a whale).

It is a bad score when you need:

- phrases (`white whale` is two terms)
- spelling variants (`haue` vs `have`, `macb` vs `macbeth`)
- a fair comparison of a 38 KB poem to a 4 MB bible (raw TF already
  divides by length, but rare-word chance still scales with size)

The tiny corpus exists so you can watch the formula hit exact
fractions before you trust a 57,000-row `idf.txt`.
