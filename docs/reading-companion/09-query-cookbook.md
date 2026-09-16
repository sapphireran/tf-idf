# Query cookbook

The companion ranks a query by treating the query as a bag of
tokens and each book as its already-built TF-IDF vector:

```
score(d) = (q · v_d) / (||q|| ||v_d||)
```

`q` uses raw query counts (usually 0/1). Terms that the snapshot
zeroed (`the`, `and`, `of`) never move the needle. Run any row with:

```bash
python3 examples/reading-companion/query_shelf.py white whale ahab pequod
```

Numbers below are from this checkout. `--check` locks the winner
and a minimum margin for each recipe.

## Name hashes (one book, huge margin)

These queries are private casts. They exist to show that TF-IDF on
this shelf is, first, a proper-name index.

| Query | Winner | Cosine | Runner-up | Runner-up cos |
| --- | --- | ---: | --- | ---: |
| `elinor marianne dashwood` | Sense and Sensibility | 0.7975 | Edgeworth | 0.0485 |
| `alice hatter gryphon dormouse` | Alice | 0.6754 | Milton | 0.0018 |
| `syme anarchist professor` | Thursday | 0.6452 | Ball and Cross | 0.0071 |
| `buster otter mink` | Buster Bear | 0.6123 | Bryant | 0.0114 |
| `unto israel moses david` | KJV | 0.6024 | Bryant | 0.0951 |
| `emma knightley hartfield woodhouse` | Emma | 0.5708 | Persuasion | 0.0008 |
| `brutus cassius antony caesar` | Julius Caesar | 0.5037 | Father Brown | 0.0032 |
| `flambeau priest brown` | Father Brown | 0.4823 | KJV | 0.0127 |
| `white whale ahab pequod` | Moby-Dick | 0.4773 | Bryant | 0.0248 |

Edgeworth in second place for the Dashwood query is the manners
leak (`dashwood` is private; residual shared diction plus any
accidental name collision). Bryant in second place for the Bible
query is the `david` children's-tale leak. Bryant in second place
for the whale query is leftover animal vocabulary, not a secret
cetology.

## Style detectors (several books, same family)

| Query | Ranked shelf (top) | What it detects |
| --- | --- | --- |
| `haue vpon selfe` | Hamlet 0.344, Macbeth 0.328, Caesar 0.264, then zeros | Folio consonants |
| `thee thou thy` | corridor files rise together; plays also hit | Early Modern address |
| `the and of` | every book 0.0000 | zero-IDF stopwords |

The stopword query is the most important negative example on the
shelf. Those three tokens have `idf = 0`, so every dot product is
zero. IDF already *is* the stopword list.

## Content versus printing

| Query | Winner | Why this wording |
| --- | --- | --- |
| `macbeth witches thane cawdor` | Macbeth 0.2444 | mixes name + plot nouns; still the play |
| `satan eve adam heaven` | Milton 0.3010 | names beat `thee` for retrieval |
| `manhattan pioneers chant` | Whitman 0.1858 | catalogue nouns, not `o` |

`macbeth witches thane cawdor` is weaker than a pure-name hash
because `witches` is not a top snapshot term (the Folio often says
`weyward` / other forms) and because cosine divides by a large
play-vector L2 driven by `macb`. It still wins by two orders of
magnitude.

## When a query should fail

- **Modern spelling against Folio text.** `have upon self` does
  not match `haue vpon selfe`. The plays go dark.
- **Theme words that every novel uses.** `love`, after
  tokenization, is `love` in Austen and `loue` in the Folio. You
  will not get a clean "books about love" ranking.
- **Ideas that are never a token.** There is no row for
  "free indirect style" or "cetology as encyclopedia."

## A small personal method

1. If you can name three characters, use them. You are hashing.
2. If you care about style, use the private alphabet (`haue`,
   `unto`, `o`).
3. If you care about theme, discard the top names in the atlas and
   query the residue (`thane cawdor`, `nantucket whaling`,
   `attachment acquaintance`).
4. Always glance at second place. Bryant and Edgeworth are the
   shelf's habitual leak-receivers.

`run_checks.py` replays every recipe in the name-hash table and
the Folio / stopword rows.
