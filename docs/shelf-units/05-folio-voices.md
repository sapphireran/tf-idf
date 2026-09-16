# Folio voices

The three Shakespeare files keep First Folio spellings and abbreviated
speech prefixes: `Macb.`, `La.`, `Hor.`, `Brut.`. File-level TF-IDF
scores the play. Speaker-level TF-IDF scores a voice.

```bash
python3 -m shelf_units voices shakespeare-macbeth -k 6
python3 -m shelf_units rank "vnsex spirits knife" --units voices --play shakespeare-macbeth
```

## What the splitter believes

A line that looks like `  Name. rest of verse` starts a turn. Aliases
are folded (`Macb` and `Macbeth` share a document; `Lady` and `La`
share `lady-macbeth`; `1.` / `2.` / `3.` / `All.` in *Macbeth* share
`witches`). `Enter`, `Exeunt`, and scene banners clear the current
voice. A lone `Exit Messenger.` does **not**, because Lady Macbeth's
"vnsex me here" speech continues after that stage direction with no new
prefix.

This is a study tool. It will mis-attribute a few wrapped lines. It will
not replace a TEI encoding.

## Macbeth, measured

16 voices have at least twenty words. A few tops from this checkout:

| voice | terms that rise |
| --- | --- |
| witches | bubble, cauldron, double, haile, hayle, mouncht |
| lady-macbeth | wouldst, groomes, natures, duncan |
| macduff | scotland, horror, children, slaine |
| doctor | she, her, sleep, vnnaturall |
| macduff-son | mother, swearers, birds, traitor |

The witches' list is the success case: the cauldron scene is a closed
vocabulary. Lady Macbeth's list is more mixed because she shares court
diction with everyone else; the unsexing speech is in her document
(`vnsex`, Folio spelling) even when it does not win the top-six, because
TF-IDF rewards rarity *across voices*, and `come` / `duncan` also move
around the play.

Hamlet's ghost / Horatio / Hamlet triangle and Caesar's
Brutus / Antony / Caesar triangle are wired the same way. A query
`horatio ghost denmark` lands on one of those three voices on this
checkout.

## Folio spelling is a feature

Do not "fix" `haile`, `vnnaturall`, or `vnsex` before you index if you
want to stay honest to this text. A modernized query `unsex` will miss
`vnsex`. Passage retrieval and speaker ranking both inherit that. The
personal lesson: TF-IDF matches the tokens you actually stored, not the
tokens you wish Shakespeare had typed.
