# Document vectors and similarity

Once every book is a map of `token -> tf * idf`, the collection is a set of sparse vectors in a shared vocabulary space. Comparing two books becomes comparing two vectors.

The 2014 blog post does this with a **dot product** on a tiny made-up vocabulary. The Python example here uses **cosine similarity**, which is the same dot product after each vector is length-normalized. Cosine is the better default when books differ in length as violently as Blake vs. the Bible.

## From a TSV file to a vector

The vocabulary of the corpus is the union of tokens. Assign each token a coordinate. A book becomes a vector `v` where

```
v[t] = tfidf(t, book)     if the book contains t
v[t] = 0                  otherwise
```

You never have to materialize the zeros. Store the map, and treat missing keys as 0.

## Dot product

```
dot(a, b) = sum_t a[t] * b[t]
```

Only tokens present in **both** books can contribute. A token with `idf = 0` contributes nothing anywhere, so the 221 corpus-wide words do not pull books together.

That is the John / Mary / Kendra example from the blog post: `John` is in every sentence, so its weight is 0, and two sentences that share only `John` have dot product 0.

## Cosine

```
cosine(a, b) = dot(a, b) / (|a| * |b|)
```

where `|v| = sqrt(sum_t v[t]^2)`.

Cosine is 1 for identical directions, 0 for no shared weighted vocabulary, and it never goes negative here because all weights are `>= 0`.

## What you should expect on this sample

Because the strongest weights are proper names and author-specific spellings, cosine on these tables is only sometimes authorship detection:

- The three Shakespeare plays *do* sit near each other. `haue`, `vpon`, and `vs` are a shared Folio dialect with `df = 3`, and speech-prefix overlap is enough to put all three pairs in the global top four.
- The three Austen novels do **not** form the tightest cluster. Each novel's top weights are character names that do not repeat, so *Emma* is as close to Edgeworth as it is to *Persuasion*. Shared period words (`mr`, `mrs`) have mid-range `idf` and cannot outrun unique casts.
- Alice is isolated: `alice`, `gryphon`, `duchess`, and `dormouse` barely leave the book. Her nearest neighbor scores are around 0.03.
- Milton, Blake, Whitman, and the Bible share `thee` / `thou` / `heaven` and therefore sit closer than theme would suggest.
- A query of distinctive names (`white whale ahab pequod`, `emma harriet knightley`) still retrieves the right book, because those strings carry almost all of the query vector.

Run:

```bash
python3 examples/python/similarity.py --tfidf-dir output/tfidf --top 12
```

The worked note [../examples/worked/neighbors.md](../examples/worked/neighbors.md) reads the resulting neighbor list.

## Boolean vectors vs. weighted vectors

The blog post first shows a boolean vector (`1` if the word occurs). Boolean cosine on this sample would mostly measure vocabulary overlap, which is dominated by book length. Weighted cosine is closer to "do these books emphasize the same rare strings?"

Both are implemented in `examples/python/similarity.py` (`--mode tfidf` or `--mode boolean`).

## Queries

A one-line query can be treated as a tiny document:

1. Tokenize the query with the same normalizer.
2. Build `tf` against the query's own length.
3. Multiply by the **corpus** `idf` (do not recompute `idf` from the query).
4. Cosine against every book.

```bash
python3 examples/python/similarity.py \
  --tfidf-dir output/tfidf \
  --idf output/idf.txt \
  --query "white whale ahab pequod"
```

That is still not a search engine — there is no inverted index and no BM25 — but it is the natural next experiment after the 2012 tables.
