# TF-IDF, as this repo computes it

TF-IDF is a bag-of-words weighting scheme. It answers a narrow question:

> In this document, which terms are both *common here* and *uncommon across
> the rest of the collection*?

That is useful for skimming a book against a background collection, for
building a crude search index, or for feeding a cosine-similarity comparison
(see `examples/compare_documents.py`). It is not a language model, not a
topic model, and not a substitute for reading the book.

## The three pieces

### Term frequency (TF)

```
tf(t, d) = count(t, d) / tokens(d)
```

This repo uses **length-normalized** TF: raw count divided by the number of
tokens the script assigned to document `d`. A word that appears 10 times in a
1,000-token poem is treated as more characteristic than a word that appears
10 times in the King James Bible.

Other textbooks use raw count, log-scaled TF (`1 + ln(count)`), or boolean
TF (`1` if present). The Perl does none of those. If you change the TF
definition you must regenerate both `output/tf/` and `output/tfidf/`.

### Document frequency (DF)

```
df(t) = |{ d in collection : count(t, d) > 0 }|
```

DF is a per-term count of *documents*, not of occurrences. "Whale" appearing
1,000 times in *Moby-Dick* and once in *Leaves of Grass* still has `df = 2`.

`output/df.txt` stores that count and the filenames, which is why you can
see that `alice` occurs in three books, not one:

```
alice    3    chesterton-thursday.txt, carroll-alice.txt, edgeworth-parents.txt
```

Chesterton and Edgeworth mention a person or word "Alice"; they are not
Carroll sequels. DF does not care why the string appeared.

### Inverse document frequency (IDF)

```
idf(t) = ln( N / df(t) )
```

`N` is the collection size. For the checked-in tables, `N = 18`.

| df(t) | idf = ln(18 / df) | Reading |
| ---: | ---: | --- |
| 1 | 2.89037 | Term is unique to one book |
| 2 | 2.19722 | Rare (Ahab, Emma, …) |
| 3 | 1.79176 | Still selective (Alice) |
| 6 | 1.09861 | Shared by a third of the collection |
| 9 | 0.69315 | Half the books |
| 18 | 0.00000 | Collection-wide stopword behavior |

IDF is **0** when a term appears in every document. In this 18-book mix,
`the`, `and`, and `a` hit that ceiling, so they contribute nothing to TF-IDF
even though their TF is huge.

Perl's `log` and Python's `math.log` are natural log. The *base* only scales
every IDF by a constant; rankings inside a single document stay the same if
you switch to `log10`. Rankings that mix raw TF with IDF from a different
base would be wrong, which is why the two Perl scripts share one `idf.txt`.

## Putting them together

```
tfidf(t, d) = tf(t, d) * idf(t)
```

Worked number from the checked-in files, term `alice` in `carroll-alice.txt`:

```
tf    = 0.0144867549668874
idf   = 1.79175946922805          # ln(18/3)
tfidf = 0.025956780390307
```

`examples/worked-examples.md` repeats this for several terms and shows why
`gryphon` ranks high with a much smaller TF: it appears in fewer books.

## What the score is not

- **Not a probability.** Values are typically `10^-2` to `10^-6` after
  length normalization. Do not treat them as percents.
- **Not comparable across collections.** Change `N` or swap in a different
  background corpus and every IDF moves.
- **Not robust to tokenizer changes.** `Alice's` becomes `alices` after the
  Perl strips punctuation. `don't` becomes `dont`. Speech prefixes such as
  `HAM` become their own terms.
- **Not BM25.** BM25 adds TF saturation and document-length bookkeeping that
  this toy pipeline does not attempt.

## Variants you will see elsewhere

This section exists so I do not accidentally "fix" the Perl to a definition I
used in a different notebook.

| Variant | Formula | This repo? |
| --- | --- | --- |
| Inverse DF, raw | `ln(N / df)` | **Yes** (checked-in output) |
| Smoothed IDF | `ln(N / (1 + df)) + 1` | No |
| Probabilistic IDF | `ln((N - df) / df)` | No |
| Smooth+idf from sklearn | `ln((1 + N) / (1 + df)) + 1` | No |
| Plus-one TF | `count + 1` | No |
| Sublinear TF | `1 + ln(count)` if count > 0 | No |
| L2-normalized TF-IDF rows | cosine-ready unit vectors | Only in `examples/compare_documents.py`, not in `output/` |

sklearn's default is closer to the smoothed column than to this repo. If a
blog post compares a sklearn vector to `output/tfidf/`, the numbers will not
match even on the same 18 files.

## Why length normalization matters here

The King James Bible is ~821k words; Blake's poems are ~6.8k. A raw-count
TF would make almost every biblical name outrank every Blake noun simply
because the Bible is long. Dividing by `tokens(d)` puts the books on a
shared [0, 1] TF scale.

It does **not** fully remove length effects. Long books still have more
*distinct* rare words, so their TF-IDF vectors are denser. Cosine similarity
(used in the compare-documents example) is the usual next step because it
ignores vector magnitude.

## Ranking inside one document

To find "what this book is about" relative to the other 17:

1. Read `output/tfidf/<book>.txt`.
2. Sort by the numeric score, descending.
3. Ignore tokenizer wreckage (`themand`, `im`, speech prefixes) or treat it
   as a reminder that the tokenizer is naive.

Do not use `sort -k2 -n` blindly on these files. Many scores are in
scientific notation (`9.89e-05`). GNU `sort -n` does not treat that as
`9.89 × 10^-5` unless you pass `-g`. `examples/top_terms.py` parses floats
in Python and ranks correctly.

## Collection-level intuition

Think of IDF as a spotlight:

- Terms that every author uses (`the`, `said`, `have`) are darkened to 0.
- Terms that one author lives in (`queequeg`, `hartfield`, `dormouse`) stay
  bright. `gryphon` is almost in that club — only Milton shares it.
- Terms that a genre shares (`whale` is mostly Melville but not exclusive;
  `lord` floods the Bible and leaks into Milton) get a dimmer spotlight.

TF then asks how hard that term is worked *inside* the book. `alice` is both
rare-ish in the collection (`df = 3`) and extremely frequent in Carroll, so
it wins that file. `whale` is more widely leaked (`df = 6`) but Melville
says it so often that it still wins *Moby-Dick*.
