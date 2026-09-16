# Personal examples

Everything in this directory is a personal teaching extra for the
tf-idf toy repo. It does not read company data and it does not replace
the original Perl scripts.

| Path | What it is |
| --- | --- |
| [`tiny_corpus/docs/`](tiny_corpus/docs/) | Five original short essays |
| [`tiny_corpus/expected/`](tiny_corpus/expected/) | Committed TF / IDF / TF-IDF tables |
| [`tiny_corpus/README.md`](tiny_corpus/README.md) | How to read that collection |
| [`python/tfidf_lab.py`](python/tfidf_lab.py) | Reference implementation |
| [`python/run_tiny_corpus.py`](python/run_tiny_corpus.py) | Score a directory of files |
| [`python/worked_example.py`](python/worked_example.py) | Print the 3-sentence table |
| [`python/top_terms.py`](python/top_terms.py) | Rank one TSV file |
| [`python/compare_docs.py`](python/compare_docs.py) | Cosine similarity |
| [`python/inspect_gutenberg.py`](python/inspect_gutenberg.py) | Read committed `output/tfidf/` |
| [`python/make_report.py`](python/make_report.py) | Standalone HTML report |
| [`gutenberg/top_terms.md`](gutenberg/top_terms.md) | Snapshot of the historical tables |

The Python files use the standard library only.

```bash
python3 examples/python/worked_example.py
python3 examples/python/run_tiny_corpus.py
python3 examples/python/inspect_gutenberg.py --only carroll-alice.txt
```
