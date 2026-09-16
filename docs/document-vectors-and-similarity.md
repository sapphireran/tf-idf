# Document vectors and cosine similarity

The 2014 post's second half turns each `tf * idf` table into a vector and compares books with a dot product. This note writes that step down so it matches `examples/python/similar_docs.py`.

## From a table to a vector

Fix an ordered vocabulary \(V = (t_1, t_2, \ldots, t_m)\) — here, the union of tokens across the files you are comparing. Document \(d\) becomes

\[
\mathbf{v}_d = \bigl(\mathrm{tfidf}(t_1, d),\; \mathrm{tfidf}(t_2, d),\; \ldots,\; \mathrm{tfidf}(t_m, d)\bigr)
\]

with \(\mathrm{tfidf}(t, d) = 0\) when \(t\) does not occur in \(d\) **or** when \(\mathrm{idf}(t)=0\).

That second case is the post's “John” example: a token that appears in every document has weight 0 in every vector, so it contributes nothing to a dot product. You do not need to delete stopwords before comparing.

The stored files are sparse (missing row = 0). The Python script keeps a `dict` per document and only iterates shared keys.

## Boolean vs weighted

The post first shows a boolean vector (`1` if the word is present). The toy then **replaces those ones with `tf * idf`**. `similar_docs.py` is the weighted version only. Boolean overlap is a different, weaker score (it would say Alice and Thursday are related because both contain `alice`, even though Thursday uses it once).

## Dot product and cosine

The raw dot product is

\[
\mathbf{v}_i \cdot \mathbf{v}_j = \sum_{t \in V} \mathrm{tfidf}(t, i)\,\mathrm{tfidf}(t, j)
\]

Long books with large weights win that number even when the *angle* is wide. The script reports **cosine**, which is what you want for “how similar is the direction”:

\[
\cos(\mathbf{v}_i, \mathbf{v}_j) = \frac{\mathbf{v}_i \cdot \mathbf{v}_j}{\|\mathbf{v}_i\|\,\|\mathbf{v}_j\|}
\]

Range is 0 to 1 for these non-negative weights. 1 means the two books have the same relative `tf * idf` profile (not “the same plot”).

## Tiny-corpus check

The four notes in `examples/tiny-corpus/documents/` are built so the geometry is obvious:

| pair | shared weighted tokens | what you should see |
| --- | --- | --- |
| bakery morning ↔ bakery afternoon | `baker`, `bread` | highest cosine |
| ridge trail ↔ rehearsal room | `followed` | middling; one verb |
| bakery afternoon ↔ rehearsal room | `rose` | middling; one verb |
| bakery morning ↔ rehearsal room | (none with nonzero idf) | cosine 0 |

`the` and `and` appear in all four notes, so they do not help, just like `John` in the post.

```bash
python3 examples/python/tfidf_toy.py examples/tiny-corpus/documents --write-dir examples/tiny-corpus/output
python3 examples/python/similar_docs.py --table-dir examples/tiny-corpus/output/tfidf
```

Numeric expectations are in [`../examples/tiny-corpus/expected-results.md`](../examples/tiny-corpus/expected-results.md).

## Gutenberg-scale measurements

Recomputed with `tfidf_toy.py` on `gutenberg/` (\(N=18\), empties not counted). Cosine on the published `output/tfidf/` tables is the same story with slightly smaller weights.

**Highest pairs** (direction, not plot):

| cosine | pair | what is actually overlapping |
| ---: | --- | --- |
| 0.308 | *Hamlet* × *Macbeth* | Folio spelling (`haue`, `vpon`, `selfe`) plus play layout |
| 0.265 | *Paradise Lost* × *Leaves of Grass* | lyric `thee` / `thou` / `o` / `thy` |
| 0.253 | *Julius Caesar* × *Hamlet* | same Shakespeare / Folio cluster |
| 0.226 | *Julius Caesar* × *Macbeth* | same |
| 0.224 | Blake × Milton | short lyric + early-modern diction |
| 0.205 | King James Bible × Milton | biblical / early-modern diction |

**Author groups are not automatic.** Distinctive *names* are almost orthogonal across books by the same person, so cosine recovers shared *leftover style tokens*, not “this is also Austen”.

| group | within-group cosines | closer to someone else? |
| --- | --- | --- |
| Shakespeare (3 plays) | 0.226 – 0.308 | no — this is the tightest cluster |
| Austen (3 novels) | 0.067 – 0.088 | *Emma* is closer to Edgeworth (0.101) than to *Sense* (0.067) |
| Chesterton (3 books) | 0.022 – 0.052 | *The Innocence of Father Brown* is closer to Edgeworth (0.099) than to *Thursday* (0.051) |

*Emma* vs *Sense and Sensibility* is modest because `emma` / `harriet` / `knightley` and `elinor` / `marianne` / `dashwood` are different dimensions. The leftover shared novel vocabulary (`mr`, `mrs`, and a few verbs) is a much weaker signal than `haue` is for two Folio plays.

*Alice* is far from the rest of the collection (best match ≈ 0.030, against Father Brown / Edgeworth). Its top weights (`gryphon`, `dormouse`, `hatter`) barely exist elsewhere. *Moby-Dick* has a mild pull toward Whitman (0.126) and Milton (0.098) from sea / biblical diction, but Ahab's crew keeps it from joining any tight cluster.

Run:

```bash
python3 examples/python/tfidf_toy.py gutenberg --write-dir /tmp/gutenberg-tfidf
python3 examples/python/similar_docs.py --table-dir /tmp/gutenberg-tfidf/tfidf --top-pairs 15
```

A copy of these numbers (and the same-author table) lives in [`../examples/gutenberg-similarity.md`](../examples/gutenberg-similarity.md).

Or compare two committed tables without recomputing IDF:

```bash
python3 examples/python/similar_docs.py \
  --tables output/tfidf/austen-emma.txt output/tfidf/austen-sense.txt
```

That last form uses the weights as already stored. It is the right way to cite the 2012 vectors.

## What cosine will not tell you

- It is not plot similarity. *Emma* and *Sense and Sensibility* are close because of `mr`, `mrs`, `said`-less Austen syntax leftovers, and shared 19th-century novel vocabulary, not because the heroines make the same mistakes.
- It is sensitive to edition. Modern-spelling Macbeth would move away from Folio Hamlet.
- It treats `whale` and `whales` as orthogonal dimensions.
- Collection-wide zeros mean you cannot use this cosine to study function-word authorship on **these** 18 files; those dimensions are already wiped. (Authorship work usually keeps function words on purpose.)

## Sparse implementation note

You do not need to allocate an 57k-dimensional array. For cosine:

```
dot = sum(weight_i[t] * weight_j[t] for t in keys(i) ∩ keys(j))
norm_i = sqrt(sum(w*w for w in weights_i))
```

Tokens that are zero in either document (absent, or idf 0) drop out of the dot product by themselves.
