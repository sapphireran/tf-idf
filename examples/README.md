# Examples

Personal, runnable companions to the notes in `docs/`.

## Tiny corpus (finish on paper)

Three six-word files. Shared verbs and articles drop to TF-IDF 0; the nouns remain.

- [tiny-corpus/README.md](tiny-corpus/README.md)
- [tiny-corpus/walkthrough.md](tiny-corpus/walkthrough.md) — every intermediate value
- [tiny-corpus/docs/](tiny-corpus/docs/) — input
- [tiny-corpus/expected/](tiny-corpus/expected/) — TF, DF, IDF, TF-IDF tables

## Public-domain excerpts

Shorter than the full Gutenberg files, long enough that character names still beat `the`.

- [excerpts/README.md](excerpts/README.md)
- [excerpts/alice-opening.txt](excerpts/alice-opening.txt)
- [excerpts/moby-cetology.txt](excerpts/moby-cetology.txt)
- [excerpts/macbeth-witches.txt](excerpts/macbeth-witches.txt)

```bash
python3 examples/python/tfidf_example.py \
  --input-dir examples/excerpts \
  --output-dir /tmp/excerpt-tfidf
python3 examples/python/extract_top_terms.py /tmp/excerpt-tfidf/tfidf/alice-opening.txt
```

## Python helpers

- [python/README.md](python/README.md)
- `python/tfidf_example.py` — reimplementation of the two Perl scripts
- `python/extract_top_terms.py` — rank a committed or freshly written TSV

## One-shot check

```bash
bash examples/run_checks.sh
```

Recreates the tiny-corpus tables, scores the excerpts, prints the Alice contrast (excerpt vs full book), and runs the unit tests.

## Suggested follow-ups

Ideas that stay inside this personal repo: [../docs/further-experiments.md](../docs/further-experiments.md).
