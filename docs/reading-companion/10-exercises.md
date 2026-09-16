# Exercises

Work these against the snapshot and the companion scripts. Do not
re-tokenize the Gutenberg files unless an exercise says so. Answers
are in [11-answers.md](11-answers.md).

## A. Reading the tables

**A1.** `output/tfidf/carroll-alice.txt` has a row `a` with value
`0`. Write the IDF equation that forces this, and name two other
tokens that must also be zero on every book.

**A2.** `whale` has IDF `1.098612…`. How many books contain `whale`
at least once? Which book should still win a query that includes
`whale`, and why is the IDF not the ceiling `ln(18)`?

**A3.** Line 50450 of `output/idf.txt` does not parse as a float.
What is the term, and why can the companion ignore that row when
ranking books?

## B. Length and names

**B1.** Without looking at the atlas, predict which file has the
single largest TF-IDF value on the shelf. Give the term and a
one-sentence reason. Then check `length_study.py`.

**B2.** *Moby-Dick* is the second-longest file and its top term is
not a person. Explain, in the product `tf * idf`, why `whale` can
beat `ahab` even though `ahab` is almost certainly rarer on the
shelf.

**B3.** Father Brown and *Thursday* are the same author. Why is
`syme` (0.024) five times `flambeau` (0.0049)? What collection
versus novel distinction does this illustrate?

## C. Clusters

**C1.** Compute (or look up) the three intra-Shakespeare cosines
and the three intra-Austen cosines. Why is the Shakespeare mean
larger even though the plays are about different murders?

**C2.** Name the book that is the nearest neighbor of all three
Austen novels. Why does author-clustering fail here?

**C3.** Alice's nearest neighbor is only ~0.03. What would have to
be true of another file for Alice to gain a serious neighbor?

## D. Queries

**D1.** Predict the winner of `haue vpon selfe`. Predict the winner
of `have upon self`. Run both if you like; explain the difference
without running the second if you can.

**D2.** Why does `unto israel moses david` put Bryant stories in
second place rather than *Paradise Lost*?

**D3.** Write a three-token query that should retrieve Whitman and
not Milton. Write one that should retrieve Milton and not Whitman.
Check them with `query_shelf.py`.

## E. Dirt in the document

**E1.** Three of *The Ball and the Cross*'s top terms are not from
1909. Name them and say which part of the file produced them.

**E2.** Sketch a ten-line filter you could add *in front of* the
2012 tokenizer (without editing those scripts) to stop license
trailers from entering TF. Do not implement a crawler; this is a
personal shelf.

## F. A small derivation

**F1.** A token appears in every book, 100 times in book A (10,000
tokens) and 100 times in book B (100,000 tokens). What are the two
TF-IDF scores? Who "wins"?

**F2.** Same counts, but the token appears in only one of the
eighteen books. What changes? Which knob — TF or IDF — moved?

**F3.** Using only the snapshot, estimate `tf(alice, carroll-alice)`
from the published TF-IDF and the published IDF. Check against
`output/tf/carroll-alice.txt`.
