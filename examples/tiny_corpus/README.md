# Tiny corpus

Three one-line documents used by `python3 -m tfidf_toy demo` and by
`tests/test_tiny_corpus.py`.

The arithmetic is written out in [`docs/worked-example.md`](../../docs/worked-example.md).

| file | intended distinctive tokens |
| --- | --- |
| `alice.txt` | `rabbit` (twice), then `alice`, `chased` |
| `whale.txt` | `ship` (twice), then `whale`, `struck` |
| `hamlet.txt` | `ghost` (twice), then `hamlet`, `saw` |

Shared tokens `the`, `was`, and `late` have idf 0 under the raw formula
and must not appear in a top-term listing.

Do not add files to this directory without updating the worked-example
document and the unit tests: the floats there are part of the spec.
