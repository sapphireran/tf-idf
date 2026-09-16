# Python toy

A stdlib-only reimplementation of the 2012 Perl pipeline, plus the two extras the Perl scripts never grew: **rank by weight** and **cosine similarity**.

| Script | Role |
| --- | --- |
| [`tfidf_toy.py`](tfidf_toy.py) | tokenize → tf / df / idf / tf×idf; optional TSV write-out |
| [`rank_terms.py`](rank_terms.py) | sort a table the way you actually want to read it |
| [`similar_docs.py`](similar_docs.py) | cosine of those vectors |
| [`compare_rankings.py`](compare_rankings.py) | top-N overlap of a fresh score vs `output/tfidf/` |
| [`tests/`](tests/) | tiny-corpus arithmetic + tokenizer checks |

Import the helpers from this directory (the CLIs do `from tfidf_toy import …`):

```bash
cd examples/python
python3 tfidf_toy.py ../../gutenberg --write-dir /tmp/gutenberg-tfidf --top 5
python3 rank_terms.py --from-table /tmp/gutenberg-tfidf/tfidf/carroll-alice.txt
python3 similar_docs.py --table-dir /tmp/gutenberg-tfidf/tfidf --top-pairs 10 --matrix
python3 -m unittest discover -s tests -v
```

From the repo root, either `cd` as above or set `PYTHONPATH=examples/python`.

## Differences from the Perl scripts

Documented at length in [`../../docs/formula-and-implementation-notes.md`](../../docs/formula-and-implementation-notes.md). Short version:

| Topic | Perl (`tf-idf-values.pl`) | this toy |
| --- | --- | --- |
| \(N\) | `$#files` from `readdir` (includes `.` / `..`) | number of files actually tokenized |
| empty tokens | increment `word_count` | ignored unless `--count-empties` |
| product step | `tf*idf-product.pl` + Text::CSV_XS | same process, no extra module |
| ranking | none | `rank_terms.py` |
| similarity | described in the 2014 post, not in-repo | `similar_docs.py` |

Gutenberg rankings should agree with `output/tfidf/` on the **order** of the top terms. Exact floats will differ slightly because of \(N\) and the empty-token denominator.

## Why there is no sklearn here

`sklearn.feature_extraction.text.TfidfVectorizer` defaults to \(\mathrm{idf}=\ln(N/\mathrm{df})+1\) and often L2-normalizes rows. Those numbers will not match this repo or the tiny-corpus pencil work. Use this toy when the goal is “same formula as the notes”.
