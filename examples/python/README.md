# Teaching Python

Stdlib-only reimplementation of the formula this repository actually
uses. It is for the micro/tiny examples and for ranking the checked-in
Gutenberg TSVs. It is not a replacement for a search library.

## Files

| File | Role |
| --- | --- |
| `tfidf_lib.py` | Tokenizer, TF, IDF, TF-IDF, TSV writers |
| `compute_tfidf.py` | CLI: directory of documents → `tf/`, `idf.txt`, `df.txt`, `tfidf/` |
| `top_terms.py` | CLI: rank a TSV file or a directory of TSV files |

Run them from the repository root, or from this directory. The CLIs
import `tfidf_lib` as a sibling module, so `examples/python/` needs to
be on `sys.path` (running the script by path does that automatically).

## Compute a collection

```bash
python3 examples/python/compute_tfidf.py \
  --input-dir examples/micro-corpus \
  --output-dir /tmp/micro-tfidf
```

```bash
python3 examples/python/compute_tfidf.py \
  --input-dir examples/tiny-corpus \
  --output-dir /tmp/tiny-tfidf
```

`--count-empty-tokens` switches on the original Perl denominator
quirk (empty `split` fields count toward document length). Leave it
off unless you are matching `tf-idf-values.pl` on a file with leading
spaces.

## Rank scores

```bash
python3 examples/python/top_terms.py /tmp/tiny-tfidf/tfidf --top 8
python3 examples/python/top_terms.py output/tfidf --top 10
```

## Formula reminder

```
tf    = raw_count / words_in_document
idf   = ln(N / df)
tfidf = tf * idf
```

`N` is the number of non-hidden `*.txt` files in `--input-dir`.
`README.md` files next to a toy corpus are notes, not documents.
Hidden names (`.DS_Store`) are skipped the same way the Perl skips `^\.`.

Full writeup: [../../docs/tf-idf-explained.md](../../docs/tf-idf-explained.md).
