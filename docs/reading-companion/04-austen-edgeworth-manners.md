# Austen, Edgeworth, and the manners cluster

Jane Austen's three novels do **not** form the tightest author
cluster on the shelf. Each is dominated by a private cast, so their
pairwise cosines sit in a modest band:

| Pair | Cosine |
| --- | ---: |
| Emma ↔ Persuasion | 0.0879 |
| Persuasion ↔ Sense | 0.0676 |
| Emma ↔ Sense | 0.0675 |
| **intra-Austen mean** | **0.0743** |

Maria Edgeworth's *The Parent's Assistant* is closer to every Austen
than the Austens are to each other:

| Pair | Cosine |
| --- | ---: |
| Persuasion ↔ Edgeworth | **0.1189** |
| Sense ↔ Edgeworth | **0.1138** |
| Emma ↔ Edgeworth | **0.1009** |

That is the most useful surprise on the prose side of the shelf.

## Why Austen does not self-cluster

Top terms are almost pure cast lists:

| Emma | Persuasion | Sense and Sensibility |
| --- | --- | --- |
| emma 0.01043 | elliot 0.00881 | elinor 0.01503 |
| harriet 0.00713 | wentworth 0.00663 | marianne 0.00906 |
| weston 0.00698 | anne 0.00587 | dashwood 0.00545 |
| knightley 0.00614 | musgrove 0.00385 | jennings 0.00494 |
| elton 0.00579 | russell 0.00311 | mrs 0.00359 |
| mr 0.00418 | mrs 0.00283 | willoughby 0.00325 |
| fairfax 0.00367 | charles 0.00276 | lucy 0.00290 |
| woodhouse 0.00365 | uppercross 0.00267 | brandon 0.00282 |
| hartfield, churchill, highbury | kellynch, lyme, harville | ferrars, barton |

Those names do not recur across novels. Cosine only sees the
leftover shared mass: `mrs`, `mr`, `herself`, `miss`, `feelings`,
`attachment`, `acquaintance`, `agreeable`. That residue is real —
it is the diction of free-indirect courtship prose — but it is
quiet compared with `elinor`.

Edgeworth's file is a *collection* of moral tales. No single
heroine can spike the way Elinor does (`cecilia` is only 0.00268).
What remains is the same social vocabulary Austen uses when she is
not saying a proper name: titles, feelings, acquaintance, the
machinery of the moral novel. A long, name-diluted collection
therefore matches the *shared* Austen layer better than *Emma*
matches *Sense and Sensibility*.

## Shared Austen terms that are not names

Minimum weight across the three novels:

| Term | Emma | Persuasion | Sense | Note |
| --- | ---: | ---: | ---: | --- |
| mrs | 0.00352 | 0.00283 | 0.00359 | married social space |
| have | 0.00152 | 0.00129 | 0.00125 | common verb; IDF is already small (`ln(18/15) ≈ 0.182`) |
| mr | 0.00418 | 0.00180 | 0.00088 | *Emma* is especially "Mr."-heavy |
| herself | 0.00068 | 0.00077 | 0.00085 | free-indirect center |
| miss | 0.00121 | 0.00049 | 0.00057 | unmarried social space |
| feelings | 0.00037 | 0.00053 | 0.00036 | the actual theme word |
| attachment | 0.00038 | 0.00038 | 0.00036 | period sense: affection / engagement |
| acquaintance | 0.00032 | 0.00059 | 0.00042 | how plots start |
| agreeable | 0.00040 | 0.00058 | 0.00026 | moral-aesthetic adjective |

`feelings` and `attachment` are the closest this snapshot comes to
admitting that the books are about interiority. They will never win
a top-ten list against `knightley`.

## Queries that isolate one novel

Because the casts are private, a three-name query is almost a hash
of the file:

```
emma knightley hartfield woodhouse     → Emma        0.5708
elinor marianne dashwood               → Sense       0.7975
```

*Persuasion* behaves the same way with `wentworth kellynch anne`.
Cross-talk is tiny (the Emma query's second place is Persuasion at
0.0008 — residual `woodhouse`-less overlap, essentially noise).

## How to read Austen on this shelf

- Use the top fifteen as a **map of places and people**, not as a
  theme extractor.
- Use Edgeworth as the **stylistic neighbor**, not Chesterton or
  Melville.
- If you want a theme word, sort the TF-IDF file and keep walking
  until you pass the last proper name. `hartfield` and `highbury`
  are still map. `feelings` is the book.

`cosine_map.py --group austen` reprints the intra-author numbers.
`query_shelf.py elinor marianne dashwood` is the Sense hash.
