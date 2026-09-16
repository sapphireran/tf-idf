# Examples

Personal study extras for the Gutenberg tf-idf toy. Nothing here is required to rerun the original Perl scripts.

| Path | What it is |
| --- | --- |
| [`toy-corpus/`](toy-corpus/) | Four one-line documents (`cats`, `dogs`, `space`, `pets`) |
| [`worked-example.md`](worked-example.md) | Every tf, df, idf, and tf-idf on that corpus, worked by hand |
| [`tfidf_mini.py`](tfidf_mini.py) | The same formula in Python, with an explicit \(N\) |
| [`run_toy_example.py`](run_toy_example.py) | Prints the intermediate tables |
| [`test_toy_example.py`](test_toy_example.py) | Asserts the hand calculation |
| [`top_terms.py`](top_terms.py) / [`top_terms.pl`](top_terms.pl) | Rank a committed `output/tfidf/` file |
| [`compare_documents.py`](compare_documents.py) | Shared vs distinctive high-scoring terms |
| [`term_report.py`](term_report.py) | One term’s df, idf, tf, and per-document tf-idf |
| [`cosine_similarity.py`](cosine_similarity.py) | Pairwise cosine on toy vectors or `output/tfidf/` |
| [`add_a_document.py`](add_a_document.py) | Add `more-cats.txt` and watch the cat/fish tie break |
| [`collection-design.md`](collection-design.md) | Why \(N\) and the file list *are* the model |
| [`sample-sessions/`](sample-sessions/) | Captured rankings from the committed Gutenberg tables |
| [`reading-sample-sessions.md`](reading-sample-sessions.md) | Guided tour of those captured lists |
| [`test_helpers.py`](test_helpers.py) | Smoke tests for the ranking scripts against `output/` |

## Toy corpus

```bash
python3 examples/run_toy_example.py
python3 examples/test_toy_example.py
```

Expected shape (see the worked note for the exact floats):

- `the` scores 0 everywhere.
- `cats.txt` ties `cat` and `fish` at the top.
- `dogs.txt` ties `dog`, `log`, and `bones`.
- `space.txt` is a flat list of unique content words.
- `pets.txt` wrongly elevates `and` alongside `play` — that is the stopword lesson.

`tfidf_mini.py` uses \(N =\) “files actually read.” That is the definition used in the docs. The original Perl pass uses `$#files` after `readdir` ([../docs/known-quirks.md](../docs/known-quirks.md)).

## Ranking the Gutenberg snapshot

From the repository root:

```bash
python3 examples/top_terms.py output/tfidf/carroll-alice.txt --n 15
perl examples/top_terms.pl output/tfidf/shakespeare-macbeth.txt 10

python3 examples/compare_documents.py \
    output/tfidf/carroll-alice.txt \
    output/tfidf/shakespeare-macbeth.txt \
    --n 12

python3 examples/term_report.py alice whale haue macb

python3 examples/cosine_similarity.py --toy
python3 examples/cosine_similarity.py --matrix --n 12
python3 examples/add_a_document.py
```

`top_terms.py` accepts any `term<TAB>number` file, so you can rank `output/tf/` as well and see how much idf changes the order.

## Regenerating sample sessions

```bash
python3 examples/top_terms.py output/tfidf/carroll-alice.txt --n 20 \
    > examples/sample-sessions/alice-top-20.txt
python3 examples/top_terms.py output/tfidf/shakespeare-macbeth.txt --n 20 \
    > examples/sample-sessions/macbeth-top-20.txt
python3 examples/top_terms.py output/tfidf/melville-moby_dick.txt --n 20 \
    > examples/sample-sessions/moby-dick-top-20.txt
python3 examples/top_terms.py output/tfidf/shakespeare-hamlet.txt --n 20 \
    > examples/sample-sessions/hamlet-top-20.txt
python3 examples/compare_documents.py \
    output/tfidf/carroll-alice.txt \
    output/tfidf/shakespeare-macbeth.txt \
    --n 15 \
    > examples/sample-sessions/comparison-alice-vs-macbeth.txt
```

Those files are checked in so you can read rankings without running anything. Refresh them if you regenerate `output/`.

```bash
python3 examples/cosine_similarity.py --matrix --n 15 \
    > examples/sample-sessions/cosine-top-pairs.txt
```
