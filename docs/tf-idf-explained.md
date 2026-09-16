# What tf-idf is doing

Term frequency–inverse document frequency is a scoring trick from information retrieval. It answers a narrower question than “which words appear often?”

> Which words appear **often in this document** and **rarely in the rest of the collection**?

That second clause is the whole point. In *Alice’s Adventures in Wonderland*, `the` is extremely common and completely useless. `alice` is also common in that file, but it barely appears in Austen, Melville, or the King James Bible. tf-idf keeps `alice` and throws `the` away.

## Two factors

### Term frequency (tf)

Raw count favors long books. *Moby-Dick* will beat *Macbeth* on almost every word simply because it has more tokens. This repo normalizes by document length:

```text
tf(t, d) = count(t, d) / tokens(d)
```

`tokens(d)` is the number of whitespace-split fields after cleaning, including some empty fields (see [known-quirks.md](known-quirks.md)). For a first reading you can treat it as “words in the file.”

A word that occupies 2% of Alice and 2% of the KJV has the same tf in both documents. Frequency alone cannot tell them apart.

### Inverse document frequency (idf)

Document frequency `df(t)` is **not** “how many times \(t\) occurs.” It is “how many documents contain \(t\) at least once.”

```text
idf(t) = ln( N / df(t) )
```

`N` is the collection size. In the committed `output/idf.txt` the largest value is

```text
ln(18) ≈ 2.89037175789616
```

which is exactly the score of a term that appears in one of the 18 Gutenberg files and nowhere else (`macbeth`, `gryphon`, `pequod`, …).

| df | idf with N = 18 | Meaning |
| --- | --- | --- |
| 1 | ln(18) ≈ 2.890 | Unique to one book |
| 3 | ln(6) ≈ 1.792 | e.g. `alice` (three files) |
| 6 | ln(3) ≈ 1.099 | e.g. `whale` |
| 18 | ln(1) = 0 | Function words such as `the` |

Because the logarithm is monotonic, any term that appears in every document is worthless as a discriminator, regardless of how often it is repeated inside a single book.

### The product

```text
tfidf(t, d) = tf(t, d) * idf(t)
```

High tf in *this* file × high idf across the collection. Either factor can kill a score:

- `the` in Alice: huge tf, idf = 0 → tf-idf = 0
- `wonderland` in Alice: tiny tf, high idf → modest score
- `alice` in Alice: large tf and a solid idf → the top score in that file (~0.026)

## A three-document cartoon

Suppose the collection is only:

1. `the cat sat on the mat`
2. `the dog sat on the log`
3. `rockets fly to the moon`

`the` appears in all three documents → idf 0.
`sat` and `on` appear in two documents → middling idf.
`cat`, `dog`, `rockets`, `moon` appear in one document → high idf.

After the product, document 1 is about `cat`/`mat`, document 2 about `dog`/`log`, document 3 about spaceflight. That is the entire method.

The same cartoon, with four documents and every intermediate number written out, is in [`../examples/worked-example.md`](../examples/worked-example.md).

## What tf-idf is not

- **Not a topic model.** It does not discover latent themes. It reweights a bag of words.
- **Not sentiment or style.** Austen’s `emma` scoring high does not mean the book is “about names”; it means the name is a good *identifier* for that file in *this* collection.
- **Not comparable across collections.** Change the 18 books and every idf changes. `whale` is moderately rare here only because most of the other files are not sea stories.
- **Not the same as sklearn / Lucene / Elasticsearch defaults.** Those systems often use:

  ```text
  tf'  = 1 + ln(count)          # log tf
  idf' = ln( (1+N) / (1+df) ) + 1
  ```

  plus sublinear tf, document-length cosine, and stopword lists. This toy does none of that.

## Why a Gutenberg pocket corpus is a good demo

The 18 files are stylistically different (plays, a novel about a whale, a children’s book, scripture, lyric poetry). Distinctive proper names and setting words jump out. If you built a corpus of eighteen Austen novels, `emma` would stop being rare and the ranking would collapse onto finer lexical habits. Collection design *is* the idf.

## Next

- Pipeline and file formats: [pipeline.md](pipeline.md)
- The actual 18 texts: [corpus.md](corpus.md)
- Reading the committed numbers: [interpreting-results.md](interpreting-results.md)
