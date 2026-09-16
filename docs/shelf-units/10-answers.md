# Answers

These were checked on this checkout. If a ranking moves after you add
notes or change a splitter, believe the new run.

## 1. Hand arithmetic

`N = 3`.

- `cat` in d1: `(3/4) * ln(3/1) ≈ 0.8240`
- `milk` in d1: `(1/4) * ln(3/2) ≈ 0.1014`
- `bread` in d3: `(2/2) * ln(3/1) ≈ 1.0986`

`tests/test_weights.py` asserts the same identities.

## 2. The 2012 `N` quarrel

18 book files + `.` + `..` = 20 directory entries. Perl `$#files` is 19.
`output/idf.txt` stores `2.89037175789616` for `00`, which is `ln(18)`,
so the **snapshot** used `N = 18` even though the current script would
feed `$#files` into `log`. The vanished blog and the fossil tables agree
with the file count, not with the live `readdir` expression.

## 3. File grain vs chapter grain

File grain answers "which Gutenberg file?" and should put
`carroll-alice` first. Chapter grain answers "which chapter of Alice?"
and puts `alice-vii` first (score ≈ 0.50) with `alice-xi` second (≈ 0.31)
because the Hatter testifies at the tarts trial. Pig and Pepper is a
distant third via `mad`.

## 4. Bible aliases

`The First Book of Samuel` is immediately followed by `Otherwise
Called:` / `The First Book of the Kings`. A matcher that treats every
`The First Book of the Kings` line as 1 Kings will cut Samuel at the
alias and lose `Ramathaimzophim`. That name belongs to **1 Samuel**.
The kit skips alias lines, including the blank line between the marker
and the title.

## 5. A bad Genesis query

`begat methuselah ark` loses to a genealogy-heavy book (1 Chronicles on
this checkout) because `begat` is cheap there. `laban rachel rebekah
esau` elects Genesis. Rare proper names beat a high-df verb.

## 6. Folio recall

The line is `That tend on mortall thoughts, vnsex me here,`. Stored
token: `vnsex`. A query with `vnsex` (and maybe `spirits`, `knife`) can
see Lady Macbeth. A modernized `unsex me here` will miss the token
unless you rewrite the text.

```bash
python3 -m shelf_units rank "vnsex spirits knife" --units voices --play shakespeare-macbeth
```

## 7. Commonplace control

Examples that win here:

```bash
python3 -m shelf_units commonplace "channeling portafilter blonding"
python3 -m shelf_units commonplace "queenright varroa brood"
```

If you query `anemone` (singular) for the tide-pool note, you can lose
to another note. That is the tokenizer, not the ranking.

## 8. Passage stride

With overlap (`stride=40`) the top two *Alice* hits for the twinkle song
are adjacent windows (14400:14480 and 14440:14520) with scores ≈ 0.71
and ≈ 0.66. With `stride=window` those neighbors no longer share tokens
and you usually get one song hit plus a farther scene. Overlap is a
smoothing choice, not extra evidence.

## 9. Milton's `th`

`th'` loses the apostrophe and becomes `th`. Book I piles up `th'`
constructions. A fix: treat `'` as a splitter, or map `th` + next token.
A reason not to: the 2012 tables fused the same way, and a "fix" would
make study-mode vectors incomparable to `output/tfidf/milton-paradise.txt`.

## 10. A thirteenth note

Whatever you add, any content word you repeat that already exists on the
shelf loses idf for everyone. If you write about a color enlarger,
`enlarger` in `01-darkroom` should drop. Rerun the commonplace command
and look at the top-term list before and after. Keep the note only if
you also keep a query test; otherwise the control experiment drifts.
