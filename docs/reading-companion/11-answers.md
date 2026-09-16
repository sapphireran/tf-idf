# Answers

## A. Reading the tables

**A1.** `idf(t) = ln(N / df(t))` with `N = 18`. If `df(t) = 18`,
`idf = ln(1) = 0`, so `tfidf = 0` regardless of TF. `the` and `and`
are the other two advertised zeros; any other token present in all
eighteen files behaves the same.

**A2.** `ln(18 / df) = 1.098612…` ⇒ `18 / df = e^1.098612… = 3` ⇒
`df = 6`. Six books mention `whale`. *Moby-Dick* still wins a whale
query because its TF is much larger than the other five. The IDF is
not `ln(18)` because the word is not private.

**A3.** The term is `thatyou` (a smashed pair). The numeric field
is `2.89037175789616y`. Book vectors live in `output/tfidf/`, which
already stores the product. Ranking never rereads that IDF line.

## B. Length and names

**B1.** `buster` in `burgess-busterbrown.txt` (0.04035). Short
children's file, incantatory private name, `df = 1`.

**B2.** `whale` has a higher TF in *Moby-Dick* than `ahab` does —
the animal and the industry are named more often than the captain.
Even with a smaller IDF (`df = 6` versus a near-hapax name), the
product still favors `whale` (0.00494 vs 0.00432). Rarity is not
the only knob.

**B3.** *Thursday* is one novel that repeats Syme. Father Brown is
a bundle of stories; `flambeau` recurs but no name is said for
70,000 words at Burgess frequency. Collections mute the top spike.

## C. Clusters

**C1.** Shakespeare: 0.3084, 0.2529, 0.2261 (mean 0.2625). Austen:
0.0879, 0.0676, 0.0675 (mean 0.0743). The plays share a private
orthography (`haue`, `vpon`, `selfe`) and speech-prefix genre.
Austen shares only quiet social diction; each cast is private.

**C2.** Edgeworth. Her file is name-diluted moral-tale prose, so
cosine sees the shared `mrs` / `feelings` / `acquaintance` layer
instead of `elinor` versus `emma`.

**C3.** Another file would need a non-trivial bag of *Alice*-private
tokens (gryphon, dormouse, hatter, …) or a large shared residue
after IDF. Ordinary Victorian prose is not enough; those pairs sit
near 0.01–0.03.

## D. Queries

**D1.** `haue vpon selfe` → Hamlet (then Macbeth, Caesar).
`have upon self` → not the plays, because those strings are not
the Folio tokens. Modern spelling misses the private alphabet.

**D2.** Bryant contains a David story (`david` is a top Bryant
term). Milton shares `thee`/`thou` with the KJV but not `israel` /
`moses` / `david` at children's-tale volume. The query is a name
mix that Bryant partially matches.

**D3.** Example pair that works on this snapshot:

- Whitman, not Milton: `manhattan pioneers chant`
- Milton, not Whitman: `satan eve adam`

Margins are in the cookbook.

## E. Dirt in the document

**E1.** `ebook`, `gutenberg`, `ebooks`. They come from the Project
Gutenberg trailer that starts around "End of Project Gutenberg's
The Ball and The Cross" (near line 9228), not from Chesterton's
chapters.

**E2.** A personal filter: if a line matches
`^\*\*\* END OF THE PROJECT GUTENBERG` or `^End of Project Gutenberg`,
stop reading that file. Optionally also skip a leading
`^\[.*Project Gutenberg` block. Apply the cut in a wrapper that
writes stripped copies into a temp dir, then point the 2012 scripts
at the temp dir. Do not mutate the checked-in `gutenberg/` files.

## F. A small derivation

**F1.** IDF is `ln(18/18) = 0`. Both scores are 0. Nobody wins.

**F2.** IDF becomes `ln(18) ≈ 2.890`. Book A: `(100/10000)*2.890 =
0.0289`. Book B: `(100/100000)*2.890 = 0.00289`. A wins by 10×.
Only IDF moved from zero to the ceiling; the TF ratio was already
10× and now it is visible.

**F3.** `tfidf = tf * idf` ⇒ `tf = tfidf / idf`.
`tfidf(alice, Alice) ≈ 0.025957`, `idf(alice) ≈ 1.791759` ⇒
`tf ≈ 0.014487`. That matches the `alice` row in
`output/tf/carroll-alice.txt` within rounding.
