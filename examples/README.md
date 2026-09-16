# Examples

Personal extras on top of the original Perl snapshot. Nothing here talks to
a network. The first two scripts only read `output/`. The tiny corpus is
self-contained.

| Path | What it does |
| --- | --- |
| [worked-examples.md](worked-examples.md) | Longhand arithmetic for `alice`, `gryphon`, `whale`, `emma`, `the` using the checked-in tables |
| [top_terms.py](top_terms.py) | Rank a book (or every book) by TF-IDF |
| [compare_documents.py](compare_documents.py) | Cosine similarity between TF-IDF vectors |
| [tiny-corpus/](tiny-corpus/) | Four short documents, a Python TF-IDF, and a hand calculation |
| [check_snapshot.py](check_snapshot.py) | Assert the frozen `output/` tables still match the worked examples |

## Run from the repository root

```bash
python3 examples/top_terms.py --n 10
python3 examples/top_terms.py --doc melville-moby_dick --n 15 --show-tf --show-idf
python3 examples/compare_documents.py --a carroll-alice --b austen-emma
python3 examples/compare_documents.py --matrix
python3 examples/tiny-corpus/compute_tfidf.py
python3 examples/tiny-corpus/test_compute_tfidf.py
python3 examples/check_snapshot.py
```

The Python programs are stdlib-only (`argparse`, `math`, `pathlib`).
