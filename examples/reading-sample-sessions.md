# Reading the captured Gutenberg rankings

The files in [`sample-sessions/`](sample-sessions/) are stdout from the helpers, frozen against the committed `output/` tree. This note is a tour of what they show. Run the same commands if you want to feel that the numbers are not hand-waved.

## Alice looks like a story; Macbeth looks like a prompt book

`alice-top-20.txt` is the poster-child result:

```text
1  alice        0.02596
2  gryphon      0.00455
3  dormouse     0.00424
4  duchess      0.00424
5  hatter       0.00371
```

Proper names and one-off creatures. `herself` and `im` (`I'm` after the apostrophe died) leak into the teen ranks because the tokenizer is a regex.

`macbeth-top-20.txt` is the honest result for an old-spelling play:

```text
1  macb     0.02156    # speech prefix
2  haue     0.01190    # "have"
3  macbeth  0.00976
4  macd     0.00913    # Macduff's prefix
5  rosse    0.00771
```

`hamlet-top-20.txt` repeats the pattern (`ham`, `hor`, `laer`, `ophe`). If you only ranked *Macbeth* you might think the script was broken. Two plays later you see a **format effect**: dramatic texts print the speaker more often than any theme word.

`comparison-alice-vs-macbeth.txt` has an empty shared window. The two bags of high-weight terms do not overlap at all. That is tf-idf doing collection-relative work, not a claim that the books have nothing in common as English.

## Novels with a hero’s name

`emma-top-20.txt` is almost a cast list: emma, harriet, weston, knightley, elton, woodhouse, fairfax. `mr` and `mrs` survive because Austen uses the honorific constantly and the other files do not (Chesterton and Burgess are not an 1810s marriage plot). idf is sociological here.

`moby-dick-top-20.txt` mixes the animal (`whale`, `sperm`, `whales`, `whaling`) with the crew (`ahab`, `stubb`, `queequeg`, `starbuck`) and the ship (`pequod`). `moby` itself is only rank 12 — Melville says “whale” far more often than “Moby.”

## One term across the collection

`term-alice-whale-haue.txt` is the useful “wait, is this word actually unique?” check.

| term | df | where the mass is |
| --- | --- | --- |
| alice | 3 | Almost all tf-idf sits in `carroll-alice.txt` |
| whale | 6 | *Moby-Dick* dominates; the KJV, Hamlet, Whitman still mention whales |
| haue | 3 | Only the three Shakespeare files, high tf in each |
| macb | 1 | *Macbeth* only — a perfect identifier and a terrible “theme” |

`whale` having df 6 is why its idf is only `ln(18/6) = ln 3 ≈ 1.099`. It still wins inside *Moby-Dick* because the tf is huge. Rarity is not required if frequency is loud enough.

`haue` is the old-spelling lesson in one line: three plays, zero novels. A modernized corpus would move that weight onto `have`, which then collides with every other English file and falls toward zero.

## Cosine is inherited baggage, not a plot detector

`cosine-top-pairs.txt` ranks every pair of the 18 vectors. The top of that list is not “same author”:

```text
0.308  hamlet × macbeth
0.265  paradise lost × leaves of grass
0.253  caesar × hamlet
0.224  blake × milton
0.205  kjv × milton
```

Open any of those pairs with `cosine_similarity.py FILE FILE` and the overlapping dimensions are Early Modern function words (`thee`, `thou`, `haue`, `hath`, `thy`). Shakespeare plays are close because they are the same *edition family*. Milton is close to the KJV for the same reason.

Austen × Austen is only ~0.07–0.09, in the same band as Austen × Edgeworth. Chesterton × Chesterton can be as low as 0.02: unique names ate the vector. Burgess’s *Buster Bear* is nearly orthogonal to the plays (~0.0002), which is the one pair the geometry gets obviously right.

Use cosine here as a sanity check on the representation, not as a recommendation engine.

## How far to trust a top-20

Treat these lists as **file identifiers** for this 18-document mix:

- Good at: “which book is this?”
- Bad at: “what is this book about?” once the file is a play, a lyric, or scripture
- Always relative: add eighteen more sea stories and `whale` sinks

The toy corpus in [`worked-example.md`](worked-example.md) is the same math with numbers you can finish on paper. The Gutenberg lists are what happens when the documents get long, old, and formatted.
