# Exercises

Work these against this checkout. Do not peek at
[10-answers.md](10-answers.md) until you have a number or a document id
in your notes. Commands assume the repository root.

## 1. Hand arithmetic

Three documents:

```
d1: cat cat cat milk
d2: dog dog milk
d3: bread bread
```

Compute classic `tf * ln(N/df)` for `cat` in d1, `milk` in d1, and
`bread` in d3. Then check `TfIdfIndex` on the same strings.

## 2. The 2012 `N` quarrel

How many entries does `readdir("gutenberg")` return on this tree,
including `.` and `..`? What is `$#files` in Perl for that array? What
idf does `output/idf.txt` actually store for a `df = 1` token such as
`00`? Write one sentence about which `N` the snapshot used.

## 3. File grain vs chapter grain

Run:

```bash
python3 -m shelf_units rank "hatter hare tea" --units gutenberg -k 3
python3 -m shelf_units rank "hatter hare tea" --units chapters --stem carroll-alice -k 3
```

What question does each ranking answer? Why does chapter XI appear in
the second list?

## 4. Bible aliases

Without reading the splitter source, find the lines around `The First
Book of Samuel` in `gutenberg/bible-kjv.txt`. Why would a title matcher
that keys on `The First Book of the Kings` open 1 Kings too early? Which
book should contain `Ramathaimzophim`?

## 5. A bad Genesis query

`begat` is a Genesis word and a Chronicles word. Predict which book
wins `begat methuselah ark` and which wins `laban rachel rebekah esau`.
Then run both.

## 6. Folio recall

Search `gutenberg/shakespeare-macbeth.txt` for the unsexing speech.
What is the stored token? Write a query that should rank
`shakespeare-macbeth:lady-macbeth` and a query that should miss her.

## 7. Commonplace control

Using only `examples/commonplace/README.md`, invent a three-word query
for the espresso note and one for the hive note. Run them. If either
loses, explain whether the problem is the query, the tokenizer, or the
note.

## 8. Passage stride

Retrieve `twinkle` in *Alice* with `--window 80 --stride 80` and again
with `--stride 40`. What happens to the top two hits when windows
overlap?

## 9. Milton's `th`

Why does `th` rank at the top of *Paradise Lost* Book I in this kit?
Propose a tokenizer change that would fix it, and one reason not to
make that change if your goal is to stay comparable to 2012.

## 10. Add a thirteenth note

Write a new commonplace file about something that is *not* already on
the shelf (a bicycle headset, a sourdough starter, a tax form — your
week). Predict two terms whose idf will fall, rerun
`python3 -m shelf_units commonplace`, and delete or keep the note as you
like. If you keep it, add a test.
