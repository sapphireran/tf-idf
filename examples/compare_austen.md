# Comparing two Austen novels

`tfidf_toy compare` subtracts per-term tf-idf inside the **same**
18-book collection. It answers:

> Relative to this shelf, which tokens are this file’s signature and not
> the other file’s?

Run:

```bash
python3 -m tfidf_toy compare --input gutenberg austen-emma.txt austen-sense.txt --k 12
```

You should see names from *Emma* (Woodhouse, Harriet, Knightley, Elton,
Hartfield) with a large positive delta against *Sense and Sensibility*,
and Elinor, Marianne, Dashwood, Willoughby, Barton on the other side.

Terms that both books share with similar density (`mrs`, `mr`, and a
long tail of ordinary verbs) fall toward delta ≈ 0 and drop out of the
top of the list.

## Why this is different from running tf-idf on two files only

If the collection were *only* those two novels, idf would be
\(\ln(2/\mathrm{df})\):

- a word in both books would score 0
- a word in one book would score \(\ln 2 \approx 0.693\) times its tf

That is a valid pairwise contrast, but it also zeros *every* shared
Austen-ism (`miss`, `sister`, `feeling`, `marriage`). Putting both novels
back on the 18-book shelf keeps those words alive when they are rare in
Melville or the KJV, and still lets character names dominate the delta
list because they are unique *and* frequent.

Try the two-file version on the tiny corpus:

```bash
python3 -m tfidf_toy compare --input examples/tiny_corpus alice.txt hamlet.txt
```

`the` / `was` / `late` stay at 0; `rabbit` vs `ghost` take the top
deltas. That run is small enough to check against
[`docs/worked-example.md`](../docs/worked-example.md).

## Other pairs worth printing

```bash
# Captain vs heroine in Persuasion vs Emma
python3 -m tfidf_toy compare --input gutenberg austen-persuasion.txt austen-emma.txt --k 10

# Whale vs prince
python3 -m tfidf_toy compare --input gutenberg melville-moby_dick.txt shakespeare-hamlet.txt --k 10

# Two Chestertons
python3 -m tfidf_toy compare --input gutenberg chesterton-thursday.txt chesterton-brown.txt --k 10
```

Speaker-tag noise in the Shakespeare file will show up here too
(`ham`, `haue`). That is expected; see
[`docs/gutenberg-results.md`](../docs/gutenberg-results.md).
