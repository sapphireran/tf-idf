# Shakespeare: speech prefixes beat character names

The three play files in `gutenberg/` are old-spelling texts with **speaker
tags** in front of many lines (`MACB.`, `HAM.`, `BRU.`). After the tokenizer
in [`../docs/tokenizer-and-quirks.md`](../docs/tokenizer-and-quirks.md)
those tags become short lowercase tokens. They are repeated on almost every
speech, and in this 18-document sample they are usually unique to one play.
TF-IDF then does exactly what it is designed to do: it promotes them.

This is not a failure of the formula. It is a reminder that the “terms” are
strings, not people.

## *Macbeth*

| Rank | Term | TF-IDF | What it is |
| ---: | --- | ---: | --- |
| 1 | `macb` | 0.02156 | speaker tag for Macbeth |
| 2 | `haue` | 0.01190 | old spelling of *have* (shared with the other two plays) |
| 3 | `macbeth` | 0.00976 | the name, in dialogue and stage directions |
| 4 | `macd` | 0.00913 | speaker tag for Macduff |
| 5 | `rosse` | 0.00771 | Ross, old spelling |
| 6 | `vpon` | 0.00566 | *upon* |
| 7 | `vs` | 0.00536 | *us* |
| 8 | `banquo` | 0.00535 | the name |
| 9 | `lenox` | 0.00441 | Lennox |
| 10 | `mal` / `thane` | 0.00393 | Malcolm’s tag / the title |
| 12 | `banq` | 0.00378 | Banquo’s tag |

`macb` has `df = 1` and a higher TF than the full name, because the file
labels the speaker more often than anyone says “Macbeth.” `macbeth` is also
`df = 1` in this sample — the other plays do not mention him — so the gap is
purely in-document frequency.

`haue` is shared by all three Shakespeare files (`df = 3`, idf ≈ 1.792). It
still ranks second in *Macbeth* because the spelling is dense. A modernized
text would have `have` instead, and `have` is almost certainly `df = 18`
(TF-IDF 0).

## *Julius Caesar*

| Rank | Term | TF-IDF | What it is |
| ---: | --- | ---: | --- |
| 1 | `bru` | 0.02082 | Brutus speaker tag |
| 2 | `brutus` | 0.01666 | the name (`df = 2`; also *Hamlet*) |
| 3 | `cassi` | 0.01456 | Cassius tag |
| 4 | `haue` | 0.01240 | *have* |
| 5 | `cassius` | 0.01157 | the name |
| 6 | `antony` | 0.00776 | the name |
| 7 | `caesar` | 0.00725 | the name (`df = 8` — widely quoted) |
| 8 | `caes` | 0.00531 | Caesar tag |
| 9 | `vs` | 0.00523 | *us* |
| 10 | `brut` | 0.00504 | another Brutus abbreviation |
| 11 | `heere` | 0.00472 | *here* |
| 12 | `caska` | 0.00435 | Casca, old spelling |

The title character **loses to his assassin’s speech prefix**. `caesar` is
famous enough to appear in eight files in this tiny sample, so IDF is only
`ln(18/8) ≈ 0.811`. Brutus the token is both more local and (as `bru`) more
frequent.

## *Hamlet*

| Rank | Term | TF-IDF | What it is |
| ---: | --- | ---: | --- |
| 1 | `ham` | 0.01408 | Hamlet speaker tag — **but `df = 5`** |
| 2 | `haue` | 0.01022 | *have* |
| 3 | `hor` | 0.00681 | Horatio tag |
| 4 | `qu` | 0.00584 | Queen tag |
| 5 | `laer` | 0.00565 | Laertes tag |
| 6 | `ophe` | 0.00528 | Ophelia tag |
| 7 | `pol` | 0.00462 | Polonius tag |
| 8 | `rosin` | 0.00405 | Rosencrantz fragment |
| 9 | `selfe` | 0.00391 | *self* |
| 10 | `loue` | 0.00380 | *love* |
| 11 | `horatio` | 0.00377 | the name |
| 12 | `vs` | 0.00362 | *us* |

`ham` is a collision: the play uses it as a prefix, and other books use
`Ham` as an ordinary token (Chesterton, KJV, *Sense*, Edgeworth). DF = 5
lowers the IDF to ≈ 1.281. The prefix still wins inside *Hamlet* because it
is printed constantly.

`hamlet` the full name has `df = 6` and a much smaller TF (people say the
prefix more than they address him by name). It does not crack this top 12.

## Shared old spelling vs. unique tags

| Token | df | Plays that use it | Typical fate |
| --- | ---: | --- | --- |
| `haue` | 3 | all three | high rank in each play |
| `vs` | 3 | all three | mid-high rank |
| `vpon` | varies | *Macbeth* especially | mid rank |
| `macb` | 1 | *Macbeth* | #1 in that file |
| `bru` | 1 | *Caesar* | #1 in that file |
| `ham` | 5 | *Hamlet* + prose | #1 in *Hamlet*, weaker IDF |
| `caesar` | 8 | widely quoted | mid rank even in *Caesar* |

TF-IDF cannot tell “this is markup” from “this is content.” A one-line
pre-pass that dropped all-caps speaker tags would flip these lists toward
`macbeth`, `brutus`, `horatio`. The 2012 scripts do not have that pre-pass.

## Tiny-corpus analogue

The accidental hapax `a` in `city-market.txt` is the same class of bug: a
string that is structurally uninteresting but locally unique. On 21 tokens
it is obvious. On a play, it looks like literary insight until you notice
`MACB.` in the source.

## Command

```bash
python3 examples/rank_top_terms.py --dir output/tfidf --file shakespeare-macbeth.txt --k 12
python3 examples/rank_top_terms.py --dir output/tfidf --file shakespeare-caesar.txt --k 12
python3 examples/rank_top_terms.py --dir output/tfidf --file shakespeare-hamlet.txt --k 12
```
