# Formula variants

The Perl scripts implement one point in a large design space. This page
lists the forks you will meet in libraries and papers, and which ones
this repo actually ships.

## IDF

| name | formula | in this repo |
| --- | --- | --- |
| raw (Sparck Jones style, as coded here) | `log(N / df)` | default (`--idf raw`) |
| smoothed (sklearn default shape) | `log((N + 1) / (df + 1)) + 1` | `--idf smooth` |
| probabilistic | `log((N - df) / df)` | not implemented |
| constant | `1` (i.e. TF only) | not implemented |

Raw IDF is 0 for a term that appears in every document. That is why
`output/tfidf/carroll-alice.txt` has zeros for `a` and `about`.

Smoothed IDF never hits zero. Try it on the three-line corpus:

```bash
python3 -m tfidf top examples/hand-calculation/corpus --idf raw --n 5
python3 -m tfidf top examples/hand-calculation/corpus --idf smooth --n 5
```

The ranking usually stays similar on a tiny collection. The difference
shows up when you start using the vectors as features: smooth IDF keeps
a little mass on collection-wide words, which can help or hurt depending
on the classifier.

## TF

| name | formula | in this repo |
| --- | --- | --- |
| length-normalized | `count / tokens` | yes (Perl and Python) |
| raw count | `count` | no |
| binary | `1` if present | no |
| sublinear (log TF) | `1 + log(count)` | no |
| BM25-style saturation | `tf * (k+1) / (tf + k * (1 - b + b * |d|/avgdl))` | no |

Length-normalized TF already dampens long Gutenberg files. Sublinear TF
would dampen `unto` in the King James Bible further; BM25 would add a
second length prior. Those are the right next experiments if you are
ranking search results rather than listing keywords.

## Normalization of the vector

The committed tables are **not** L2-normalized. A document with a large
unique vocabulary can have a larger Euclidean norm than a short file
even after TF is length-normalized.

`tfidf.compute.cosine_sparse` L2-normalizes on the fly when it scores
pairs or queries. The TSV files themselves stay unnormalized so they
remain comparable to `output/tfidf/`.

sklearn's `TfidfVectorizer` default is smoothed IDF **and** L2
normalization. Do not expect its `.idf_` array to match `output/idf.txt`.

## Stopwords, stems, n-grams

The 2012 scripts keep every token. That is why `mr` and `mrs` rank high
in Austen and why `unto` / `thee` / `thou` dominate the Bible and
Milton. Adding an English stopword list would hide those and promote
more content words. Stemming would merge `whale` / `whales` /
`whaling` in *Moby-Dick* (they currently appear as three terms).

Bigrams (`great red`, `sperm whale`) are a different representation. This
toy pipeline is unigram-only.

## Query scoring

Search engines rarely use raw document TF-IDF as the final rank. A
minimum useful ranking function, which the Python CLI implements, is:

1. Fit IDF on the corpus.
2. Build a TF-IDF vector for the query with the same IDF table.
3. Score each document by cosine similarity.

```bash
python3 -m tfidf query examples/tiny-corpus "mooring barnacles jib"
```

Terms that never appeared in the corpus are dropped. There is no
query-length discount beyond ordinary TF, and there is no field boost
(title vs body). Treat it as a teaching aid, not a search product.

## Practical advice

- Use **raw IDF + top terms** when you want to explain a document to a
  person, the way this repo's Gutenberg tables do.
- Use **smoothed IDF + L2** when the vectors are features for a linear
  model.
- Use **BM25** when you are ranking a query against many documents and
  care about length saturation.
- Always say which variant you used. "We used TF-IDF" is not a complete
  sentence.
