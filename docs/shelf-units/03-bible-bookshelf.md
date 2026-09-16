# The King James file as a bookshelf

`gutenberg/bible-kjv.txt` is 99,805 lines and about 821,000 words. In the
2012 run it is one document. That makes `jesus`, `lord`, `unto`, and
`israel` compete with `whale` and `alice` at file scale, and it makes
*Jonah* invisible as a book.

This kit splits the file into **55 units**: 54 titled books plus one
bundle for the twelve minor prophets, which this particular dump never
labels.

```bash
python3 -m shelf_units bible -k 6
python3 -m shelf_units bible --book genesis -k 8
python3 -m shelf_units rank "pharaoh egypt passover" --units bible
python3 -m shelf_units compare genesis exodus --units bible
```

## How the split is conservative

The NLTK text uses real title lines for most Protestant books, then a
pair of alias conventions that will fool a naive scanner:

```
The First Book of Samuel

Otherwise Called:

The First Book of the Kings
```

and later

```
The First Book of the Kings

Commonly Called:

The Third Book of the Kings
```

2 Kings repeats the same pattern with "The Fourth Book of the Kings".
`shelf_units.split_bible` consumes primary titles in order and skips
whatever sits after `Otherwise Called:` / `Commonly Called:`, including
the blank line this dump likes to put in between. Ezra is the one-word
title `Ezra`, matched only as a whole line so a genealogy fragment does
not open a new book.

Hosea through Malachi have no titles. After Daniel 12 the next `1:1`
starts a unit called `hosea-malachi`. That unit is a compromise, and it
is documented as one: TF-IDF cannot invent book boundaries the file
refused to print. Jonah still lights up a query for `nineveh great fish
jonah` because those words are rare on the rest of the shelf. You just
cannot ask the index "Jonah versus Micah".

## Measured tops (classic `ln(N/df)`, `N = 55`)

Genesis, from this checkout:

| term | tf-idf |
| --- | ---: |
| laban | 0.00416 |
| abram | 0.00380 |
| jacob | 0.00346 |
| joseph | 0.00334 |
| esau | 0.00310 |
| rachel | 0.00292 |
| rebekah | 0.00282 |

Exodus:

| term | tf-idf |
| --- | ---: |
| moses | 0.00519 |
| sockets | 0.00421 |
| aaron | 0.00390 |
| pharaoh | 0.00368 |
| egypt | 0.00270 |
| twined | 0.00248 |

`sockets` and `twined` are the tabernacle inventory, not theology. That
is the method working: the distinctive *written* stuff in Exodus includes
furniture instructions.

Largest gaps, Genesis vs Exodus:

| term | genesis | exodus |
| --- | ---: | ---: |
| moses | 0 | 0.00519 |
| sockets | 0 | 0.00421 |
| laban | 0.00416 | 0 |
| aaron | 0 | 0.00390 |
| abram | 0.00380 | 0 |
| esau | 0.00310 | 0 |

Queries that elect the obvious book on this checkout:

| query | winner |
| --- | --- |
| `pharaoh egypt passover` | `exodus` |
| `nineveh great fish jonah` | `hosea-malachi` |
| `laban rachel rebekah esau` | `genesis` |

A sloppy query such as `begat methuselah ark` loses to 1 Chronicles,
because Chronicles is a machine for `begat`. Units fix filing. They do
not fix a query that is mostly a high-df verb.

## What file-level TF-IDF could not say

At the 2012 grain, the entire KJV is one vector. `pharaoh` is a moderately
interesting term in a giant religious document. At book grain, `pharaoh`
is an Exodus word that barely exists in Genesis after Joseph, and `laban`
is a Genesis word that Exodus forgets. Same formula. Different shelf.
