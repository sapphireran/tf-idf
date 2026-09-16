# Tiny corpus

Three seven-token documents. Every count in [walkthrough.md](walkthrough.md) can be done with a pencil.

```
cats.txt    cats sit on mats / cats chase mice
dogs.txt    dogs sit on mats / dogs chase cats
birds.txt   birds fly over trees / birds chase insects
```

`chase` appears in all three files, so it is this toy's `the`: `idf = ln(3/3) = 0`.
`cats` appears in two files, so it is this toy's `alice`.
`mice` appears in one file, so it is this toy's `dormouse`.

## Files

| Path | Role |
| --- | --- |
| `docs/*.txt` | The three documents |
| `expected/` | Tables written by `examples/python/run_pipeline.py` |
| `walkthrough.md` | Tokenization, `tf`, `df`, `idf`, `tf * idf`, cosine |

## Recompute

```bash
python3 examples/python/run_pipeline.py \
  --input examples/tiny-corpus/docs \
  --output /tmp/tiny-tfidf

diff -u examples/tiny-corpus/expected/idf.txt /tmp/tiny-tfidf/idf.txt
```
