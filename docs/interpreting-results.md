# Interpreting the committed results

The tables under `output/` are alphabetical, so the interesting words are not at the top of the file. Rank by the numeric second column.

```bash
python3 examples/top_terms.py output/tfidf/carroll-alice.txt --n 10
```

Do not use `sort -k2` without telling `sort` to use general numeric mode (`-g`). Values such as `8.26e-05` will otherwise interleave wrongly with `0.025…`.

## Alice in Wonderland

From `output/tfidf/carroll-alice.txt` and the matching tf / idf rows:

| term | tf (Alice) | idf | tf-idf |
| --- | --- | --- | --- |
| alice | 0.01449 | 1.79176 | **0.02596** |
| turtle | (low) | high | 0.00566 |
| hatter | … | high | 0.00371 |
| gryphon | … | ~ln(18) | 0.00455 |
| dormouse | … | high | 0.00424 |
| rabbit | … | medium | 0.00178 |
| wonderland | tiny | high | 0.00025 |
| the | ~0.05 | **0** | **0** |

`alice` wins because it is frequent *and* only appears in three of the 18 files (`idf = ln(18/3) = ln 6 ≈ 1.792`). `wonderland` is a perfect identifier in spirit but almost does not occur in the body (the title header is most of its count), so tf-idf stays small. `the` is the most common token and the worst possible identifier.

`rabbit` is less rare across English prose than `gryphon`, so a fairly common word loses to a rarer creature.

## Macbeth

| term | tf-idf |
| --- | --- |
| macbeth | 0.00976 |
| thane | 0.00393 |
| banquo | 0.00535 |
| duncan | 0.00157 |
| macduff | 0.00142 |
| witches | 0.00078 |

The play identifies itself with its cast. Shared Shakespearean function words (`thou`, `thee`, `lord`) are discounted because Hamlet and Caesar (and Milton, and the KJV) also use them.

`macbeth` has `idf = ln(18) ≈ 2.890` — it is unique to this file in the pocket corpus. That is an artifact of collection design, not a linguistic law. Add *Macbeth* criticism or another edition and the idf drops.

## Moby-Dick

| term | tf-idf | idf note |
| --- | --- | --- |
| whale | 0.00494 | idf ≈ 1.099 = ln(3) → six files mention `whale` |
| ahab | 0.00432 | rarer name |
| sperm | 0.00326 | sperm whale |
| pequod | 0.00165 | unique ship name, lower tf |
| nantucket | 0.00130 | place name |
| ishmael | 0.00019 | famous, but not frequent in the token stream |

`whale` outranks `ahab` on tf-idf even though `ahab` is the more “plot-specific” name, because Melville says `whale` constantly. idf only *reweights*; it does not replace frequency. `ishmael` is a reminder that cultural salience and tf-idf are different things — the narrator names himself rarely.

## Cross-document comparison

`examples/compare_documents.py` takes two `output/tfidf/` files and prints:

- terms that score highly in both (shared texture)
- terms that score highly in A but not B
- terms that score highly in B but not A

Alice vs Macbeth is almost disjoint on the top 20: `alice`/`hatter`/`gryphon` versus `macbeth`/`banquo`/`thane`. That is the method working. Alice vs Bryant’s children’s stories will share more ordinary words (`little`, `said`-adjacent leftovers after idf) and is a better stress test.

## When a high score is a footnote

- **OCR / join artifacts.** `themand` in Alice is almost certainly an em-dash or comma disappearing between `them` and `and`. High idf (unique typo) × tiny tf can still sneak into a mid-list if you rank naively.
- **Numerals.** `1865`, verse numbers in the KJV, and `1`, `2`, `3` from chapter headings all get scores. They are rarely meaningful.
- **Speaker labels in plays.** `macbeth` is both character and speech prefix. tf is inflated by the script format. That is legitimate for *identifying the file*; it is misleading if you wanted “themes of the play.”
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
