# Examples

Personal, runnable companions to the Gutenberg snapshot. Nothing here is company code or a service.

| Path | What it is for |
| --- | --- |
| [hand-calculation.md](hand-calculation.md) | Three sentences, every intermediate float. Start here if you want to check the formula on paper. |
| [tiny-corpus/](tiny-corpus/) | Five original short documents, a Python calculator, and a checked-in raw TSV snapshot. |
| [top_terms.py](top_terms.py) | Sort any `term<TAB>score` directory (Gutenberg `output/tfidf` or the tiny-corpus output). |

Typical session:

```bash
python3 -m unittest discover -s tests -v
python3 examples/tiny-corpus/compute_tfidf.py --explain tea
python3 examples/tiny-corpus/compute_tfidf.py --stop --no-write --n 6
python3 examples/top_terms.py --files carroll-alice.txt --n 10
```
