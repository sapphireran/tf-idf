# Chapter walks

Four splitters live in `shelf_units.split_chapters`:

| stem | heading | units on this checkout |
| --- | --- | ---: |
| `carroll-alice` | `CHAPTER I.` … indented `CHAPTER XII` | 12 |
| `milton-paradise` | `Book I` … `Book XII` | 12 |
| `melville-moby_dick` | `ETYMOLOGY.` / `EXTRACTS` / `CHAPTER n` | 137 |
| `austen-emma` (also persuasion, sense) | `CHAPTER` + roman numeral | 55 / 24 / 50 |

```bash
python3 -m shelf_units chapters carroll-alice -k 5
python3 -m shelf_units rank "mad hatter march hare tea" --units chapters --stem carroll-alice
python3 -m shelf_units chapters milton-paradise -k 4
```

## Alice, chapter by chapter

The 2012 file-level table buries the Hatter in a novel-length denominator.
At chapter grain the cast walks in and out:

| unit | title | top terms (this checkout) |
| --- | --- | --- |
| alice-i | Down the Rabbit-Hole | bats, key, cake, candle |
| alice-ii | The Pool of Tears | mouse, swam, mabel, pool |
| alice-iii | A Caucus-Race and a Long Tale | dodo, mouse, prizes, lory, thimble |
| alice-iv | The Rabbit Sends in a Little Bill | window, puppy, chimney, bottle, fan |
| alice-v | Advice from a Caterpillar | caterpillar, pigeon, serpent, youth, eggs |
| alice-vi | Pig and Pepper | footman, baby, cat, pig, mad |
| alice-vii | A Mad Tea-Party | dormouse, hatter, hare, march, twinkle |
| alice-viii | The Queen's Croquet-Ground | queen, gardeners, hedgehog, soldiers |
| alice-ix | The Mock Turtle's Story | turtle, mock, gryphon, moral, duchess |
| alice-x | The Lobster Quadrille | turtle, mock, gryphon, dance, join |
| alice-xi | Who Stole the Tarts? | hatter, king, court, witness, dormouse |
| alice-xii | Alice's Evidence | king, jury, dream, sister, verses |

Chapter XII is titled on the next line in this dump (`CHAPTER XII` /
`Alice's Evidence`). The splitter peeks forward for that.

A query `hatter hare tea` ranks:

| score | unit |
| ---: | --- |
| 0.503 | alice-vii A Mad Tea-Party |
| 0.315 | alice-xi Who Stole the Tarts? |
| 0.055 | alice-vi Pig and Pepper |

That second-place trial chapter is not a mistake. The Hatter is a
witness. File-level TF-IDF cannot tell those two scenes apart.

## Paradise Lost

Milton's twelve books keep the argument visible:

| unit | distinctive-ish terms |
| --- | --- |
| paradise-i | height, temple (plus a fused `th` from `th'`) |
| paradise-vi | fight, armed, chariot |
| paradise-ix | eve, tasting, adam |
| paradise-x | death, curse, hiss, bruise |
| paradise-xii | moses, abraham, canaan |

`th` winning Book I is the tokenizer again: `th'` + `the` debris after
punctuation stripping. Chapter units make that scar *louder*, because a
short book has less competing vocabulary. See
[08-formula-and-quirks.md](08-formula-and-quirks.md).

## Moby-Dick

The file has 135 numbered chapters plus `ETYMOLOGY.` and `EXTRACTS`.
Chapter 1 still contains Ishmael. The etymology unit is a word-hoard and
will rank strangely for nautical jargon queries — it is a glossary
pretending to be a chapter, which is another reminder that "unit" is a
literary decision.

## Austen

`CHAPTER` + roman numerals. Emma's first unit still contains Woodhouse.
These splitters exist so you can ask "which chapter of *Emma*?" without
pretending the novel is one bag of manners words.
