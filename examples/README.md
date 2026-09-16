# Examples

Personal, hand-written study texts. Nothing here is scraped and
nothing here comes from a workplace.

## `tiny_corpus/`

Four one-sentence-pair documents built so the arithmetic in
[`notebook/04-worked-example-tiny-corpus.md`](../notebook/04-worked-example-tiny-corpus.md)
can be done on paper:

| File | About | Distinctive tokens I planted |
| --- | --- | --- |
| `doc_cats.txt` | A cat on a mat | `cat`, `mat`, `sun`, `rooms` |
| `doc_dogs.txt` | A dog on a log | `dog`, `log`, `walks` |
| `doc_kitchen.txt` | A cook and an oven | `cook`, `oven`, `bread`, `soup`, `kitchen` |
| `doc_stars.txt` | A night sky | `stars`, `telescopes`, `night`, `light` |

Shared furniture (`the`, `sat`, `and`, `likes`, `warm`, `quiet`,
`fields`) exists on purpose so IDF is not `log N` for every word.

```bash
python3 -m tfidf demo
python3 -m tfidf rank "cat mat" --corpus tiny
python3 -m tfidf rank "distant telescopes" --corpus tiny
```

## Gutenberg queries I use as a smoke test

These are not a relevance study. They are sentences I would be
embarrassed to get wildly wrong after touching the ranker.

```bash
python3 -m tfidf rank "white whale ahab" --corpus gutenberg --k 3
python3 -m tfidf rank "alice rabbit queen" --corpus gutenberg --k 3
python3 -m tfidf rank "macbeth witches thane" --corpus gutenberg --k 3
```
