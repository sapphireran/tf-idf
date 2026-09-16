# Measured Gutenberg similarities

Numbers from:

```bash
python3 examples/python/tfidf_toy.py gutenberg --write-dir /tmp/gutenberg-tfidf --top 0
python3 examples/python/similar_docs.py --table-dir /tmp/gutenberg-tfidf/tfidf --top-pairs 20
python3 examples/python/compare_rankings.py --corpus gutenberg --committed-dir output/tfidf --top 10
```

`compare_rankings.py` reported **1.00 top-10 overlap** and the same #1 term for every book against `output/tfidf/`. The Python toy is telling the same ranking story as the 2012 tables; only the floats move a little (`|d|` does not count empty split leftovers).

## Closest books (cosine of `tf * idf`)

| cosine | pair |
| ---: | --- |
| 0.3084 | `shakespeare-hamlet.txt` × `shakespeare-macbeth.txt` |
| 0.2654 | `milton-paradise.txt` × `whitman-leaves.txt` |
| 0.2529 | `shakespeare-caesar.txt` × `shakespeare-hamlet.txt` |
| 0.2261 | `shakespeare-caesar.txt` × `shakespeare-macbeth.txt` |
| 0.2244 | `blake-poems.txt` × `milton-paradise.txt` |
| 0.2049 | `bible-kjv.txt` × `milton-paradise.txt` |
| 0.1583 | `blake-poems.txt` × `whitman-leaves.txt` |
| 0.1265 | `melville-moby_dick.txt` × `whitman-leaves.txt` |
| 0.1189 | `austen-persuasion.txt` × `edgeworth-parents.txt` |
| 0.1138 | `austen-sense.txt` × `edgeworth-parents.txt` |

The Shakespeare trio is the only same-author group that wins on cosine. The next band is **shared early-modern / lyric diction** (Milton, Whitman, Blake, KJV), not “same novelist”.

## Same-author pairs

| pair | cosine | note |
| --- | ---: | --- |
| Hamlet × Macbeth | 0.3084 | Folio spelling + play tokens |
| Caesar × Hamlet | 0.2529 | same |
| Caesar × Macbeth | 0.2261 | same |
| Emma × Persuasion | 0.0879 | different casts |
| Persuasion × Sense | 0.0676 | different casts |
| Emma × Sense | 0.0675 | different casts |
| Father Brown × Thursday | 0.0510 | different casts |
| Ball × Father Brown | 0.0523 | different casts |
| Ball × Thursday | 0.0222 | different casts |

*Emma* is closer to Edgeworth's *Parent's Assistant* (0.1009) than to *Sense and Sensibility* (0.0675). That is expected once you look at the ranked terms: `emma` and `elinor` cannot match, while `mr` / `mrs` and other 19th-century novel leftovers can.

## Far-away books

*Alice* vs the rest of the collection tops out around 0.030. *Buster Bear* and the Shakespeare plays vs Austen sit near 0.001–0.007. Unique names plus a small leftover stoplist make a very sparse geometry.

The write-up of why this happens is in [`../docs/document-vectors-and-similarity.md`](../docs/document-vectors-and-similarity.md).
