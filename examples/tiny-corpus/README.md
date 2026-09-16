# Tiny teaching corpus

Three six-word documents. Every tf, idf, and tf-idf value is written out
in [`docs/worked-example.md`](../../docs/worked-example.md) and stored in
[`expected.json`](expected.json).

| File | Text |
| --- | --- |
| `cats.txt` | the cat sat on the mat |
| `dogs.txt` | the dog sat on the log |
| `birds.txt` | a bird flew over the lake |

```bash
python3 examples/python/tfidf.py --input examples/tiny-corpus --top 6
```
