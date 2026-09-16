# What `tf * idf` is doing in this repo

This note matches the **published** Gutenberg tables: 18 books, natural log, raw term frequency (count / document length). It is the same family of weights as the 2014 post [Build your own search Engine](https://rutumulkar.com/ml-notes/information%20retrieval/lucene/2014/05/20/build-your-own-search-engine.html). Variants used in Lucene, BM25, or sklearn are called out only where they would change a number you can see in `output/`.

## Two counting problems

A term is useful for telling documents apart when it is:

1. **Frequent in this document** — otherwise it is not really “about” the document.
2. **Rare across the collection** — otherwise every document has it and it cannot rank or cluster anything.

Term frequency (`tf`) measures (1). Inverse document frequency (`idf`) measures (2). Their product is the weight stored in `output/tfidf/*.txt`.

## Term frequency

For a token \(t\) in document \(d\):

\[
\mathrm{tf}(t, d) = \frac{\mathrm{count}(t, d)}{|d|}
\]

\(|d|\) is the number of tokens after the regex cleanup in `tf-idf-values.pl` (see the README). This is *normalized* term frequency: a word that appears 10 times in a 100-token note beats a word that appears 10 times in a 10,000-token novel.

In *Alice's Adventures in Wonderland* the committed table says:

| token | `tf` |
| --- | ---: |
| `the` | 0.0613 |
| `and` | 0.0318 |
| `alice` | 0.0145 |
| `gryphon` | 0.0021 |

Raw frequency loves `the`. That is expected, and it is why `tf` alone is a poor keyword list.

## Inverse document frequency

Let \(N\) be the number of documents (18 in `output/`) and \(\mathrm{df}(t)\) the number of those documents that contain \(t\) at least once:

\[
\mathrm{idf}(t) = \ln\frac{N}{\mathrm{df}(t)}
\]

Perl's `log` and Python's `math.log` are both natural log. That is why a hapax-in-the-collection such as `macbeth` has

\[
\ln(18/1) = 2.89037175789616
\]

which is exactly the line in `output/idf.txt`.

A few values from the published IDF table:

| token | `df` | `idf` | why |
| --- | ---: | ---: | --- |
| `the`, `and`, `of`, `if`, `when`, `a` | 18 | `0` | present in every book |
| `whale` | 6 | \(\ln(18/6)=\ln 3 \approx 1.099\) | several books mention whales |
| `alice` | 3 | \(\ln(18/3)=\ln 6 \approx 1.792\) | Alice, Thursday, and Edgeworth |
| `gryphon` | 2 | \(\ln(18/2)=\ln 9 \approx 2.197\) | almost Alice-only |
| `macbeth` | 1 | \(\ln 18 \approx 2.890\) | only the play |

`df` for `alice` is 3, not 1. The name also appears in Chesterton's *The Man Who Was Thursday* and Edgeworth's *The Parent's Assistant*. That is visible on the `alice` row of `output/df.txt`:

```
alice	3	chesterton-thursday.txt, carroll-alice.txt, edgeworth-parents.txt,
```

So `alice` is a strong *Alice* keyword, but it is not a collection-wide hapax.

## The product

\[
\mathrm{tfidf}(t, d) = \mathrm{tf}(t, d) \times \mathrm{idf}(t)
\]

For Alice in `carroll-alice.txt`:

\[
0.014486755 \times 1.791759469 \approx 0.02596
\]

which matches the first data row of `output/tfidf/carroll-alice.txt` (`alice  0.02595678`). `the` has a much larger `tf` and a zero `idf`, so its product is 0.

That is the whole trick of this toy: **collection-wide function words drop out because their IDF is zero, not because anyone listed them as stopwords.**

## What the ranking then looks like

Once `the` is gone, the high weights in a book are usually:

- **character and place names** (`ahab`, `pequod`, `emma`, `hartfield`, `syme`)
- **topic nouns that barely leak into the other 17 books** (`whale`, `gryphon`, `dormouse`)
- **author- or edition-specific spellings** (`haue`, `vpon`, `selfe` in the Shakespeare files)

A reading of several books is in [gutenberg-term-walkthrough.md](gutenberg-term-walkthrough.md).

## What this is *not*

This repo does **not** use:

| Variant | Who uses it | Effect |
| --- | --- | --- |
| \(\log(1 + \mathrm{count})\) or BM25 term saturation | most search engines | caps “mention it 400 times” |
| \(\mathrm{idf} = \ln\frac{N - \mathrm{df} + 0.5}{\mathrm{df} + 0.5}\) | BM25 / Lucene | never exactly 0, even for `the` |
| \(\mathrm{idf} = \ln\frac{N}{\mathrm{df}} + 1\) | sklearn `TfidfVectorizer` default | `the` still gets a small positive weight |
| stemming / lemmatization | many IR stacks | `whale` and `whales` would merge |
| a real tokenizer | spaCy, Lucene analysis | `Alice's` would not become `alices` |

Keep the published numbers aligned with the 2012 scripts. If you want BM25 or sklearn weights, that is a different experiment.

## A size you can check by hand

The Gutenberg files are too large to recompute on paper. [`../examples/tiny-corpus/`](../examples/tiny-corpus/) is four nine-token notes with the same formulas. Every `tf`, `df`, `idf`, and `tf * idf` value is written out in [`../examples/tiny-corpus/worked-example.md`](../examples/tiny-corpus/worked-example.md).
