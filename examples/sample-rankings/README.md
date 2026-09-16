# Sample rankings

Checked-in `top_terms.py` listings so the distinctive-term claim in
the docs can be read without running anything.

| File | Source |
| --- | --- |
| `tiny-top8.txt` | teaching Python over `examples/tiny-corpus/` |
| `gutenberg-top8.txt` | teaching ranker over the original Perl `output/tfidf/` |

Regenerate:

```bash
python3 examples/python/top_terms.py examples/tiny-corpus-expected/tfidf --top 8
python3 examples/python/top_terms.py output/tfidf --top 8
```
