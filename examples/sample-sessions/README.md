# Sample sessions

Captured stdout from the helper scripts against the **committed** `output/` snapshot. Refresh with the commands in [../README.md](../README.md) if those tables change.

| File | Command |
| --- | --- |
| `alice-top-20.txt` | `python3 examples/top_terms.py output/tfidf/carroll-alice.txt --n 20` |
| `macbeth-top-20.txt` | same for `shakespeare-macbeth.txt` |
| `moby-dick-top-20.txt` | same for `melville-moby_dick.txt` |
| `hamlet-top-20.txt` | same for `shakespeare-hamlet.txt` |
| `emma-top-20.txt` | same for `austen-emma.txt` |
| `comparison-alice-vs-macbeth.txt` | `compare_documents.py` Alice vs Macbeth, `--n 15` |
| `term-alice-whale-haue.txt` | `term_report.py alice whale haue macb` |
| `cosine-top-pairs.txt` | `cosine_similarity.py --matrix --n 15` |
| `cosine-named-pairs.txt` | a few author-matched and cross-genre pairs |

Read `macbeth-top-20.txt` and `hamlet-top-20.txt` side by side if you want the speech-prefix lesson without rerunning anything.
