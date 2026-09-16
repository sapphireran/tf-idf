# Examples

Personal teaching extras on top of the original Perl toy. Nothing here
talks to a network or depends on CPAN.

| Script | Role |
| --- | --- |
| `tiny_tfidf.py` | tokenize the four-document toy and write TF / DF / IDF / TF-IDF |
| `inspect_tokenize.py` | print what the toy tokenizer does to a line |
| `rank_terms.py` | highest TF-IDF terms in a precomputed table |
| `query_documents.py` | sum query-term weights across a directory of tables |
| `explain_term.py` | DF / IDF / TF / TF-IDF for one term across books |
| `compare_variants.py` | raw TF vs repo TF-IDF vs smoothed IDF on the toy |
| `run_checks.py` | smoke-test the scripts against the checked-in tables |
| `tiny-corpus/` | four original notes used by the worked example |
| `tiny-output/` | tables produced by `tiny_tfidf.py` (safe to regenerate) |

Run every command from the repository root.

## Tiny corpus

```bash
python3 examples/tiny_tfidf.py
python3 examples/tiny_tfidf.py --check
python3 examples/tiny_tfidf.py --no-write
```

`--check` asserts the four top-term scores documented in
[docs/03-worked-example.md](../docs/03-worked-example.md). If you edit the
notes in `tiny-corpus/`, update `EXPECTED_TOP` in `tiny_tfidf.py` and that
doc together.

`--corpus` and `--output` point the same math at any directory of
plain-text files:

```bash
python3 examples/tiny_tfidf.py --corpus examples/tiny-corpus --output /tmp/tiny-out
```

Do not aim `--output` at `output/` unless you intend to replace the
Gutenberg snapshot.

## Tokenizer

```bash
python3 examples/inspect_tokenize.py
python3 examples/inspect_tokenize.py "Moby-Dick; or, The Whale."
```

## Rank and query the Gutenberg snapshot

```bash
python3 examples/rank_terms.py carroll-alice --top 10
python3 examples/rank_terms.py shakespeare-hamlet --top 8
python3 examples/query_documents.py alice gryphon hatter
python3 examples/query_documents.py whale ahab pequod
```

## Explain one term

```bash
python3 examples/explain_term.py alice
python3 examples/explain_term.py whale
python3 examples/explain_term.py --root examples/tiny-output tea
```

## Compare weightings on the toy shelf

```bash
python3 examples/compare_variants.py
python3 examples/run_checks.py
```

## Rank and query the toy tables

```bash
python3 examples/rank_terms.py --dir examples/tiny-output/tfidf --top 6
python3 examples/query_documents.py --dir examples/tiny-output/tfidf tea rabbit
```

The query scorer is a sum, not cosine similarity. See
[docs/06-querying-and-ranking.md](../docs/06-querying-and-ranking.md).
