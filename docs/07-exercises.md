# Exercises

Work these on paper or with the desk. Answers are in
[08-answers.md](08-answers.md). Use classic weights and `N = 18` unless a
problem says otherwise.

## 1. Recover `N` from a hapax

A term that appears in exactly one gold file has `idf = 2.89037175789616`.
Show that this is `ln(18)`.

## 2. Alice is not a hapax

`output/df.txt` lists `alice` in three files. What is `idf(alice)`? Using
the gold TF `0.0144867549668874`, what is `tfidf(alice, Alice)`?

## 3. Why `macb` beats `macbeth`

Both strings are essentially unique to `shakespeare-macbeth.txt`. Give two
reasons the speaker tag still wins in the gold TF-IDF sort.

## 4. Empty-field denominator

A cleaned document is the single line ` cairn ice` (leading space). Raw
counts: `cairn` 1, `ice` 1. What is `word_count`? What is `tf(cairn)`?

## 5. Universal term

`the` has `df = 18`. What is its TF-IDF in *Moby-Dick*, regardless of how
often Melville wrote it?

## 6. Field-notes ranking

Without looking at the expected tables, say which of the four field notes
wins each query under cosine / classic IDF, and name the two terms you
expect to pay for the hit:

- `cairn icefall`
- `tympan quoins`
- `silica voucher`

## 7. `$#files` versus gold

This tree’s `gutenberg/` directory has 18 texts + `.DS_Store`. What `N`
would a fresh run of `tf-idf-values.pl` use? What happens to every hapax
IDF compared with gold?

## 8. Cosine versus dot

A query is the single term `whale`. Why might **dot product** prefer the
KJV or a long Chesterton novel over *Moby-Dick* less often than you fear,
and why might it still prefer *Moby-Dick*? (Hint: look at `idf(whale)` and
at raw length.)

## 9. Smooth IDF sign

For `N = 18` and `df = 18`, classic IDF is 0. What is `smooth` IDF
(`ln(N / (df + 1))`)? Why might a teaching demo keep classic for this
shelf?

## 10. Attribution sanity

You run `explain "gryphon dormouse" --doc carroll-alice.txt`. Which two
contribution rows should dominate, and why is `alice` *not* in that list
unless you add it to the query?
