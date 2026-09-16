# Length and name bias

TF-IDF on a raw shelf is a terrible "importance" score and a pretty
good "this string is glued to this file" score. The difference is
almost entirely length plus proper names.

## The headline numbers

| Book | Words | Vocab in the snapshot | Heaviest term | Weight | Vector L2 |
| --- | ---: | ---: | --- | ---: | ---: |
| Buster Bear | 15,870 | 1,568 | buster | **0.04035** | 0.04816 |
| Alice | 26,443 | 2,753 | alice | 0.02596 | 0.02847 |
| Thursday | 57,955 | 6,524 | syme | 0.02435 | 0.02607 |
| Macbeth | 17,741 | 3,560 | macb | 0.02156 | 0.03636 |
| Julius Caesar | 20,459 | 3,091 | bru | 0.02082 | 0.04292 |
| Ball and Cross | 81,598 | 8,646 | turnbull | 0.01795 | 0.02424 |
| Sense and Sensibility | 118,675 | 7,335 | elinor | 0.01503 | 0.02139 |
| Hamlet | 29,605 | 4,799 | ham | 0.01408 | 0.02862 |
| KJV | 821,133 | 16,567 | unto | 0.01204 | 0.01625 |
| Emma | 158,167 | 9,312 | emma | 0.01043 | 0.02016 |
| Persuasion | 83,308 | 5,990 | elliot | 0.00881 | 0.01701 |
| Blake | 6,845 | 1,542 | thel | 0.00558 | 0.01245 |
| Father Brown | 71,626 | 8,235 | flambeau | 0.00489 | 0.00862 |
| Moby-Dick | 212,030 | 19,961 | whale | 0.00494 | 0.01158 |
| Bryant | 45,988 | 4,011 | margery | 0.00375 | 0.00982 |
| Edgeworth | 166,070 | 9,561 | cecilia | 0.00268 | 0.00992 |
| Paradise Lost | 79,659 | 9,321 | thee | 0.00220 | 0.00752 |
| Leaves of Grass | 122,070 | 14,568 | o | 0.00183 | 0.00653 |

`buster` is not a more meaningful word than `whale`. It is a rare
token (`df = 1`, so it sits on the IDF ceiling) repeated in a short
file. `whale` is the thematic center of a long book and still
appears in five other files (`df = 6`, `idf ≈ 1.099`), so both the
numerator and the IDF are smaller.

Blake is the shortest file and does *not* win the top-term contest.
`thel` is concentrated in one poem inside a mixed pamphlet, so the
name never reaches Burgess-level repetition.

## Two knobs, one product

Write the heaviest term's score as

```
(count_in_book / book_tokens) * ln(N / df)
```

For `buster` the first factor is large because the denominator is
small and the name is incantatory. For `whale` the first factor is
diluted by cetology, legal chapters, and every sailor who is not
named Whale. For `unto` the first factor is moderate and the IDF is
only `ln(18/6) ≈ 1.099`, but the KJV is so long that a moderate TF
still produces a mid-pack weight.

This is why vector L2 tracks the top term. Burgess is a spike
(`||v|| = 0.048`). Whitman is a low ridge (`||v|| = 0.0065`): many
terms, none of them private and frequent. Cosine will later divide
by that L2, which is why a spiked children's book is *not* similar
to anything else — the spike points in a unique direction.

## Names versus content

Almost every top term on the shelf is a person, a speech prefix, or
a form of address. The exceptions are the interesting ones:

| Book | Top term | Kind |
| --- | --- | --- |
| Moby-Dick | whale | content (animal / industry) |
| KJV | unto | archaic function word |
| Paradise Lost | thee | archaic pronoun |
| Leaves of Grass | o | vocative / line-initial particle |
| Macbeth / Hamlet / Caesar | macb, ham, bru | drama speech prefixes |

If you came here hoping TF-IDF would surface "whiteness," "revenge,"
or "free indirect style," it will not. Those ideas are spread across
common verbs. The statistic lights up strings that are *unevenly
distributed*, and personal names are the most uneven strings in
narrative prose.

A useful personal habit: read the top fifteen, mentally discard
names and prefixes, and then look at what is left. After `ahab`,
`stubb`, `queequeg`, `starbuck`, and `pequod` are set aside,
*Moby-Dick* still has `sperm`, `whales`, `nantucket`, `boats`,
`whaling`, `deck`. That residue is the book. After `emma`,
`harriet`, `weston`, `knightley` are set aside, *Emma* has `mr`,
`mrs`, `hartfield`, `highbury` — still mostly the social map, not
an abstract theme.

## Drama prefixes are names in costume

The Folio texts print speech prefixes as `Macb.`, `Ham.`, `Bru.`.
The tokenizer strips the period and keeps `macb`. Those tokens are
short, frequent, and unique to one play, so they occupy the same
statistical niche as `buster`. They tell you which play you are in.
They do not tell you what the play is about. See the Folio note.

## A rule of thumb for this shelf

- Short file + repeated private name → weight in the 0.02–0.04
  range (Burgess, Alice, Thursday, the three plays).
- Long file + thematic but shared word → weight near 0.005
  (*Moby-Dick*).
- Long file + shared poetic diction → weight near 0.002 (Milton,
  Whitman).
- Collection of many stories, each with its own cast → muted top
  term (Bryant 0.0037, Edgeworth 0.0027, Father Brown 0.0049).

Father Brown is the clean illustration of the last row. Chesterton
wrote several stories in one file. `flambeau` recurs, but no single
parish name is incanted for 70,000 words. The vector stays short.
*Thursday* is one novel about Syme, so `syme` looks like `buster`.

Run `python3 examples/reading-companion/length_study.py` to reprint
the table from the snapshot.
