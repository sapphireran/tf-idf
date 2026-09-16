# Themed paragraphs

Three short documents with repeated content words. Unlike the tiny
corpus, each file has a clear winner (`baker` / `flour`, `stars` /
`telescope`, `violin` / `melody`) instead of a five-way hapax tie.

| File | Theme |
| --- | --- |
| `bakery.txt` | baker, dough, flour, cakes |
| `observatory.txt` | astronomer, telescope, stars |
| `concert.txt` | violinist, violin, melody, concert |

```bash
python3 examples/python/tfidf.py --input examples/themes-corpus --top 8
```

`examples/python/tfidf.py --input examples/themes-corpus --similar bakery.txt`
prints cosine similarity from the bakery vector to every file in the
same collection. Bakery is identical to itself (`1.0`), barely overlaps
the observatory (`fill` is the only shared content word), and is
orthogonal to the concert file: `the`, `a`, `second`, and `before` all
have `df = 3`, so `idf = 0` and they drop out of the dot product.
