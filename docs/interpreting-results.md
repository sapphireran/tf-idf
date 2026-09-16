# Interpreting the committed results

The tables under `output/` are alphabetical, so the interesting words are not at the top of the file. Rank by the numeric second column.

```bash
python3 examples/top_terms.py output/tfidf/carroll-alice.txt --n 10
```

Do not use `sort -k2` without telling `sort` to use general numeric mode (`-g`). Values such as `8.26e-05` will otherwise interleave wrongly with `0.025…`.

## Alice in Wonderland

From `output/tfidf/carroll-alice.txt` (ranked with `examples/top_terms.py`):

| rank | term | tf-idf |
| --- | --- | --- |
| 1 | alice | 0.02596 |
| 2 | gryphon | 0.00455 |
| 3–4 | dormouse, duchess | 0.00424 |
| 5 | hatter | 0.00371 |
| 6 | turtle | 0.00317 |
| 8 | rabbit | 0.00178 |
| — | wonderland | 0.00025 |
| — | the | **0** |

`alice` wins because it is frequent *and* only appears in three of the 18 files — Wonderland plus stray given-name hits in *The Man Who Was Thursday* and *The Parent’s Assistant* (`idf = ln(18/3) = ln 6 ≈ 1.792`). `examples/term_report.py alice` shows the other two tf-idf scores are two orders of magnitude smaller. `wonderland` is a perfect identifier in spirit but almost does not occur in the body (the title header is most of its count), so tf-idf stays small. `the` is the most common token and the worst possible identifier.

`rabbit` is less rare across English prose than `gryphon`, so a fairly common word loses to a rarer creature. `alices` (rank 9) is the possessive after the apostrophe is stripped — a tokenizer split, not a second character.

## Macbeth (and the other plays)

The committed *Macbeth* table does **not** open on “witches / scotland / dagger.” It opens on the play’s printed voice:

| rank | term | tf-idf | What it actually is |
| --- | --- | --- | --- |
| 1 | macb | 0.02156 | speech prefix for Macbeth |
| 2 | haue | 0.01190 | old spelling of *have* |
| 3 | macbeth | 0.00976 | the name, in full |
| 4 | macd | 0.00913 | speech prefix for Macduff |
| 5 | rosse | 0.00771 | Ross, old spelling |
| 8 | banquo | 0.00535 | the thane |
| 11 | thane | 0.00393 | the title |

Hamlet and Caesar do the same thing: `ham` / `hor` / `laer` and `bru` / `cassi` / `caes` outrank most vocabulary. These Gutenberg files are **old-spelling dramatic texts**. Speaker labels repeat on every speech, so their tf is enormous, and the abbreviations are unique to that play, so their idf is enormous too. idf is doing its job; the bag of words includes stage machinery.

Shared Early Modern spellings (`haue`, `vpon`, `vs`, `selfe`, `loue`) still score well because this pocket corpus only has three such plays plus Milton and the KJV — not enough witnesses to drive those idfs to zero.

`macbeth` as a full word has `idf = ln(18) ≈ 2.890` (unique in this collection). That is an artifact of collection design, not a linguistic law.

## Moby-Dick

| rank | term | tf-idf | note |
| --- | --- | --- | --- |
| 1 | whale | 0.00494 | idf ≈ 1.099 = ln(3) → six files mention it |
| 2 | ahab | 0.00432 | rarer name, slightly lower tf |
| 3 | sperm | 0.00326 | sperm whale |
| 4–5 | stubb, queequeg | 0.00309 / 0.00288 | crew |
| 8 | pequod | 0.00165 | unique ship name, lower tf |
| 9 | nantucket | 0.00130 | place name |
| — | ishmael | 0.00019 | famous, but not frequent in the token stream |

`whale` outranks `ahab` on tf-idf even though `ahab` is the more “plot-specific” name, because Melville says `whale` constantly. idf only *reweights*; it does not replace frequency. `ishmael` is a reminder that cultural salience and tf-idf are different things — the narrator names himself rarely.

## Cross-document comparison

`examples/compare_documents.py` takes two `output/tfidf/` files and prints:

- terms that score highly in both (shared texture)
- terms that score highly in A but not B
- terms that score highly in B but not A

Alice vs Macbeth is disjoint on the top 12: `alice`/`gryphon`/`hatter` versus `macb`/`haue`/`banquo`. That is the method working. Alice vs Bryant’s children’s stories will share more ordinary words and is a better stress test.

Novels with stable proper names look “clean” (*Emma*: emma, harriet, knightley; *Thursday*: syme, gregory, gogol). Lyric and scripture look “pronominal” (*Paradise Lost* and the KJV both elevate `thee`/`thou`/`unto`) because those words are frequent and this collection is not uniformly Early Modern.

Pairwise **cosine** on the same vectors is in `examples/cosine_similarity.py`. Shakespeare plays cluster because they share old spelling; Milton sits near the KJV for `thee`/`thou`. That geometry is documented in [formula-variants.md](formula-variants.md) and [`../examples/reading-sample-sessions.md`](../examples/reading-sample-sessions.md).

## When a high score is a footnote

- **OCR / join artifacts.** `themand` in Alice is almost certainly an em-dash or comma disappearing between `them` and `and`. High idf (unique typo) × tiny tf can still sneak into a mid-list if you rank naively.
- **Numerals.** `1865`, verse numbers in the KJV, and `1`, `2`, `3` from chapter headings all get scores. They are rarely meaningful.
- **Speaker labels in plays.** `macb`, `ham`, `bru` are prefixes printed before every speech. They dominate tf-idf because they are both frequent and file-unique. Legitimate for *identifying the file*; misleading if you wanted “themes of the play.”
- **Old spelling.** `haue`, `vpon`, `rosse`, `selfe` are not OCR errors. These editions keep Early Modern orthography. A modernized Shakespeare would rerank toward `macbeth` / `brutus` / `horatio`.
- **Author leakage.** Three Chesterton files mean Chestertonian favorites have depressed idf. A word that would look “rare” in a mixed-century corpus looks ordinary here.

## Zero means “useless in this collection”

`idf = 0` is not “the word never occurred.” It is “the word occurred in every document.” In `output/idf.txt` you will find `a`, `and`, `the` at 0. Their tf-idf lines are `0` (integer-looking) rather than a tiny float.

A missing term in a tf-idf file means that term never occurred in that document. It will still have a global idf if it occurred somewhere else.

## Sanity checks you can run

```bash
# Every committed tf-idf file has a zero row for 'the'
python3 -c "
from pathlib import Path
for p in sorted(Path('output/tfidf').glob('*.txt')):
    rows = dict(line.split('\t') for line in p.read_text().splitlines() if line.strip())
    print(f\"{p.name:30} the={rows.get('the', 'MISSING')}\")
"

# Top term should be a content word, not a preposition
python3 examples/top_terms.py output/tfidf/milton-paradise.txt --n 5
```

If you regenerate with a different \(N\), absolute scores move. Within-document *order* can also move, because changing \(N\) adds \(\mathrm{tf}(t)\cdot\ln(N_{\mathrm{new}}/N_{\mathrm{old}})\) to every score — a boost proportional to tf, which favors common terms. That is one more reason to treat \(N\) as part of the experiment, not an implementation detail.
