# tf-idf

Personal learning repo: a small, inspectable pipeline for **term frequency–inverse document frequency** (tf-idf) on a Project Gutenberg sample, plus worked examples that show the same math on a tiny original corpus.

This is not a library and not production search code. It exists so you can read every line, rerun the numbers, and see why a word that is common in one book and rare in the others rises to the top.

The original Perl scripts (`tf-idf-values.pl` and `tf*idf-product.pl`) accompany an old walkthrough of the same idea. The `docs/` and `examples/` trees expand that walkthrough: formulas, a hand calculation, a five-document toy corpus, and notes on how to read the checked-in Gutenberg scores.

## What tf-idf is doing here

For each document \(d\) and term \(t\):

\[
\mathrm{tf}(t, d) = \frac{\mathrm{count}(t, d)}{\lvert d \rvert}
\qquad
\mathrm{idf}(t) = \ln\frac{N}{\mathrm{df}(t)}
\qquad
\mathrm{tfidf}(t, d) = \mathrm{tf}(t, d) \cdot \mathrm{idf}(t)
\]

- **tf** is a within-document share: how much of this book is this word.
- **df** is a corpus count: how many books contain the word at least once.
- **idf** is large when the word is rare across the collection, and \(0\) when it appears in every document (\(N = \mathrm{df}\)).
- **tf-idf** is therefore “used a lot here, and not everywhere.”

That is why `alice` dominates *Alice’s Adventures in Wonderland*, `whale` / `ahab` dominate *Moby-Dick*, and `emma` / `harriet` dominate *Emma*, while words such as `the` and `and` collapse toward zero.

Natural log (`ln`, Perl `log`, Python `math.log`) matches the original scripts.

## Repository map

| Path | Role |
| --- | --- |
| `gutenberg/` | 18 public-domain texts used as the document collection |
| `tf-idf-values.pl` | Tokenize each file, write per-document **tf**, then corpus **df** / **idf** |
| `tf*idf-product.pl` | Multiply each term’s tf by its idf and write `output/tfidf/` |
| `output/tf/` | Normalized term frequencies, one file per book |
| `output/df.txt` | Document frequency plus the file names that contain each term |
| `output/idf.txt` | Inverse document frequency for every term |
| `output/tfidf/` | Final scores, still one file per book |
| `docs/` | Formulas, pipeline notes, corpus catalog, how to read the scores |
| `examples/tiny-corpus/` | Five short original documents and a Python calculator |
| `examples/hand-calculation.md` | Three-sentence example with every intermediate number |
| `examples/top_terms.py` | Print the highest-scoring terms from any `output/tfidf` file |

## Gutenberg collection

Eighteen files, from Blake’s poems (~1.4k lines) to the KJV Bible (~100k lines). Lengths are uneven on purpose: tf is length-normalized, so a long book does not automatically outrank a short one for a shared word.

See [docs/corpus.md](docs/corpus.md) for titles, authors, and why a few high scores are artifacts of spelling or speaker tags (`ham`, `haue`, `mr`).

## Run the original Perl pipeline

You need Perl 5 and, for the product script, [Text::CSV_XS](https://metacpan.org/pod/Text::CSV_XS).

```bash
# from the repository root
mkdir -p output/tf output/tfidf
perl tf-idf-values.pl
perl 'tf*idf-product.pl'
```

The first script prints `Processing file: …` once per book, writes `output/tf/<filename>`, then `output/df.txt` and `output/idf.txt`. The second script reads those tables and writes `output/tfidf/<filename>`.

Checked-in files under `output/` are a snapshot of an earlier run. Re-running will overwrite them. Small numeric drift is expected if your Perl `log` or directory listing order differs; the ranking of distinctive names should stay stable.

### Tokenization (same rules in Perl and in the tiny-corpus example)

1. Drop carriage returns.
2. Collapse horizontal/vertical whitespace to a single space.
3. Lowercase.
4. Strip every character that is not ASCII letter, digit, or space.
5. Split on spaces; ignore empty tokens.

Apostrophes disappear, so `Alice's` becomes `alices` and `I'm` becomes `im`. That is visible in the Alice ranking.

## Run the tiny worked example

No third-party Python packages. From the repository root:

```bash
python3 examples/tiny-corpus/compute_tfidf.py
python3 examples/tiny-corpus/compute_tfidf.py --explain tea
python3 examples/tiny-corpus/compute_tfidf.py --stop --no-write --n 6
python3 examples/top_terms.py --path examples/tiny-corpus/output/tfidf --n 8
python3 examples/top_terms.py --files carroll-alice.txt --n 10
python3 -m unittest discover -s tests -v
```

The calculator writes `examples/tiny-corpus/output/` in the same tf / df / idf / tfidf layout as the Gutenberg pipeline, and prints a ranking table to stdout. `--explain TERM` walks one term through every document.

## Documentation

1. [docs/tf-idf-explained.md](docs/tf-idf-explained.md) — intuition, formulas, and what the scores are *not*.
2. [examples/hand-calculation.md](examples/hand-calculation.md) — three documents, every count, no shortcuts.
3. [docs/pipeline.md](docs/pipeline.md) — line-level tour of the two Perl scripts, including the \(N\) quirk.
4. [docs/corpus.md](docs/corpus.md) — the eighteen books and known ranking artifacts.
5. [docs/interpreting-results.md](docs/interpreting-results.md) — how to read `output/tfidf` for Alice, *Moby-Dick*, *Hamlet*, *Emma*, and Blake.
6. [docs/gutenberg-top-terms.md](docs/gutenberg-top-terms.md) — top 10 terms for all 18 files, generated from the snapshot.
7. [docs/idf-variants.md](docs/idf-variants.md) — raw `ln(N/df)` vs smoothed / probabilistic / BM25-style idf.
7. [examples/tiny-corpus/README.md](examples/tiny-corpus/README.md) — the five-document collection and expected top terms.

## Known quirks (worth reading before you trust a number)

- **\(N\) in the Perl script.** `tf-idf-values.pl` sets `$n = $#files` on a `readdir` list that still contains `.` and `..`. That is “last index of the directory listing,” not “number of texts.” The committed `output/` snapshot behaves like \(N = 18\) (words in every book get idf \(0\)). See [docs/pipeline.md](docs/pipeline.md).
- **No stopword list.** Function words are suppressed only when they really do appear in every document. In a tiny collection they can still rank.
- **No stemming.** `whale` and `whales` are different terms; both rank in *Moby-Dick*.
- **Speaker tags and old spelling.** First Folio-style *Hamlet* scores `ham`, `haue`, `vs` alongside `hamlet` and `horatio`.
- **Zeros are meaningful.** A tf-idf of `0` is usually “this word is in every document,” not “this word is absent.”

## License / provenance

The texts under `gutenberg/` come from [Project Gutenberg](https://www.gutenberg.org/) and are public-domain in the United States. The short documents under `examples/tiny-corpus/documents/` are original examples written for this repo. Keep this tree personal and educational; it is not a product codebase.
