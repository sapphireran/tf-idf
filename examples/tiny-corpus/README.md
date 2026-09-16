# Tiny 4-document corpus

Four short, original paragraphs. They exist so the formulas in
[`../hand-calculation.md`](../hand-calculation.md) stay small enough to
recompute without a spreadsheet.

| File | Tokens | Exclusive repeated terms | Shared terms |
| --- | ---: | --- | --- |
| `docs/apple-orchard.txt` | 20 | `orchard` (2) | `apple` (also market), `blossom` (also garden), `in`, `the` |
| `docs/ocean-voyage.txt` | 18 | `whale` (2), `ship` (2) | `the` only |
| `docs/city-market.txt` | 21 | `city` (2), `market` (2), `stall` (2) | `apple`, `in`, `the` |
| `docs/night-garden.txt` | 19 | `moon` (2), `garden` (2), `night` (2) | `blossom`, `in`, `the` |

No Project Gutenberg text is copied here.

## Score it

```bash
python3 examples/tiny-corpus/compute_tfidf.py \
  --corpus examples/tiny-corpus/docs \
  --output examples/tiny-corpus/output
```

Layout matches the historical Perl pipeline. A scored copy of those tables is
committed under `output/` so you can read the numbers without running Python:

```
output/tf/<doc>.txt
output/df.txt
output/idf.txt
output/tfidf/<doc>.txt
```

`N` is the number of files actually scored (4), not Perl's `$#files`.

## Verify against the hand calculation

```bash
python3 examples/tiny-corpus/compute_tfidf.py --verify
```

The verifier rebuilds into a temp directory (or `--output` if you pass one)
and checks:

- token lengths 20 / 18 / 21 / 19
- `idf(the) == 0`, `idf(apple) == ln(2)`, `idf(orchard) == ln(4)`
- `tfidf(orchard, apple-orchard) == 0.1 * ln(4)`
- `tfidf(apple, apple-orchard) == 0.1 * ln(2)`
- voyage top terms are `ship` and `whale`
- garden top terms are `garden`, `moon`, `night`

## Expected top terms (numeric sort)

| Document | 1st | 2nd band |
| --- | --- | --- |
| apple-orchard | `orchard` | `apple` tied with other tf=0.05, df=1 words |
| ocean-voyage | `ship`, `whale` (tie) | singleton voyage words |
| city-market | `city`, `market`, `stall` (tie) | `apple` and hapax `a` in the next band |
| night-garden | `garden`, `moon`, `night` (tie) | singleton garden words; `blossom` lower |

If a change to the tokenizer breaks this, the hand-calculation page and this
verifier should fail together. Update both on purpose; do not “fix” one side
quietly.
