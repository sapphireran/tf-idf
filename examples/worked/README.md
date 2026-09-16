# Worked readings of the 2012 snapshot

These notes read the committed `output/` tables. They do not regenerate them.

| Note | Question |
| --- | --- |
| [alice-in-wonderland.md](alice-in-wonderland.md) | Why does `alice` beat `dormouse`? |
| [austen-vs-shakespeare.md](austen-vs-shakespeare.md) | Why do plays cluster and novels do not? |
| [neighbors.md](neighbors.md) | What does cosine actually retrieve here? |
| [stopwords-and-zero-idf.md](stopwords-and-zero-idf.md) | What vanished, and what unexpectedly survived? |

Commands used to produce the numbers:

```bash
python3 examples/python/rank_terms.py --tfidf-dir output/tfidf --output-root output --top 8
python3 examples/python/similarity.py --tfidf-dir output/tfidf --top 20
python3 examples/python/inspect_committed.py --token alice
```
