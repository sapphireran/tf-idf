# Public-domain excerpts

Three short slices copied from the Gutenberg files already in this repo. They exist so you can watch TF-IDF work on a collection you can read in one sitting.

| file | source in `gutenberg/` | roughly about |
| --- | --- | --- |
| `alice-opening.txt` | `carroll-alice.txt`, rabbit-hole opening | Alice, the Rabbit, a book without pictures |
| `moby-cetology.txt` | `melville-moby_dick.txt`, Ishmael + sperm-whale proclamation | Ishmael, Greenland whale vs sperm whale |
| `macbeth-witches.txt` | `shakespeare-macbeth.txt`, I.i–I.ii | witches, Macbeth, Early Modern spelling |

These are not substitutes for the 18-book run. They are a middle step between the six-word toy corpus and *Moby-Dick*.

## Run

```bash
python3 examples/python/tfidf_example.py \
  --input-dir examples/excerpts \
  --output-dir /tmp/excerpt-tfidf

python3 examples/python/extract_top_terms.py /tmp/excerpt-tfidf/tfidf/alice-opening.txt -n 12
python3 examples/python/extract_top_terms.py /tmp/excerpt-tfidf/tfidf/moby-cetology.txt -n 12
python3 examples/python/extract_top_terms.py /tmp/excerpt-tfidf/tfidf/macbeth-witches.txt -n 12
```

## What you should see

`N = 3`, so IDF is harsh: a word that appears in all three excerpts is zeroed. Everyday words that happen to miss one excerpt (`she` is Alice-heavy; `whale` is Melville-heavy; `macbeth` is the play) keep a positive IDF.

Typical heads after a run on this folder (exact floats depend on the files staying as committed):

- **alice-opening.txt** — `alice`, `rabbit`, `sister`, `pictures`, `book` rise above `the`.
- **moby-cetology.txt** — `whale`, `sperm`, `greenland`, `ishmael`, `books`.
- **macbeth-witches.txt** — `macbeth`, `thunder`, `lightning`, `witches`, plus Folio spellings (`vpon`, `raine`, `houer`).

Compare `extract_top_terms.py --tf` on the same files: `the` / `and` / `of` will lead again. That is the same contrast as [../../docs/interpreting-results.md](../../docs/interpreting-results.md), at a size you can diff in an editor.

## Provenance

Text is public-domain Project Gutenberg material already stored under `gutenberg/`. Line breaks follow those files. Do not replace these excerpts with copyrighted novels.
