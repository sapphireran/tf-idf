# Neighbors in the 18-book snapshot

153 unordered pairs. Cosine on the committed `tf * idf` vectors.

```
python3 examples/python/similarity.py --tfidf-dir output/tfidf --top 20
```

## The top of the list

| Rank | Pair | Cosine | Shared mass |
| ---: | --- | ---: | --- |
| 1 | Hamlet — Macbeth | 0.3084 | Folio spellings + dramatic function words |
| 2 | *Paradise Lost* — *Leaves of Grass* | 0.2654 | `thee`, `thou`, `thy`, vocative style |
| 3 | Caesar — Hamlet | 0.2529 | same Folio dialect as row 1 |
| 4 | Caesar — Macbeth | 0.2261 | same |
| 5 | Blake — Milton | 0.2244 | `thee` / `thou` / `heaven` |
| 6 | KJV — Milton | 0.2049 | biblical second person and `hath` |
| 7 | Blake — Whitman | 0.1583 | prophetic second person |
| 8 | *Moby-Dick* — Whitman | 0.1265 | shared 19th-century inventory, not whales |
| 9 | *Persuasion* — Edgeworth | 0.1189 | period social prose |
| 10 | *Sense* — Edgeworth | 0.1138 | same |
| 16 | *Emma* — *Persuasion* | 0.0879 | first Austen–Austen pair |

The geometry is dominated by **closed-class relics** that happen to have `df < 18`: Folio orthography, Early Modern second person, and a few speech prefixes. It is not dominated by plot.

Milton appearing next to Whitman and the Bible is the clearest example. Milton's own top weights are `thee`, `thou`, `heaven`, `thy`, `eve`, `adam`. Those are also the Bible's and Whitman's high-mass coordinates. `satan` is distinctive but not heavy enough to pull Milton away from that cluster.

## Isolated books

Alice's best cosine is 0.030. Burgess's *Buster Bear* is a children's book whose top weight is `buster` at 0.040 — unique and relentless — so it also sits apart. *The Man Who Was Thursday* is almost a one-token document at the top: `syme` at 0.024.

Isolation here is a compliment to the weighting. A book whose rare strings do not leak will not be anyone's neighbor.

## Queries are sharper than pairs

Pairwise cosine uses every non-zero coordinate, including weak mid-`idf` words. A four-word query uses only those four `idf` values.

| Query | Top hit | Cosine | Runner-up |
| --- | --- | ---: | --- |
| `white whale ahab pequod` | *Moby-Dick* | 0.4485 | Bryant 0.0115 |
| `emma harriet knightley highbury` | *Emma* | 0.6142 | *Persuasion* 0.0006 |
| `alice hatter duchess dormouse` | Alice | 0.5673 | Chesterton Brown 0.0011 |
| `macbeth banquo thane cawdor` | *Macbeth* | 0.3073 | (zero) |

`whale` itself has `df = 6` (Melville, Bible, Whitman, Bryant, Hamlet, Chesterton *Ball*). The query still works because `ahab` and `pequod` are essentially unique and carry most of the query mass.

Bryant as runner-up for the whale query is a real leak: the stories mention a whale, and `whale` is the only query token Bryant has. The cosine is 40× smaller than Melville's.

## Boolean vs weighted

```
python3 examples/python/similarity.py --tfidf-dir output/tfidf --mode boolean --top 8
```

Boolean cosine (presence of any non-zero weight) rewards long books that share ordinary vocabulary. The Bible and *Moby-Dick* have huge vocabularies, so they rise. Weighted cosine is the one that matches the blog post's "replace the 1s with `tf * idf`" step.

Use boolean only as a contrast. The committed ranking story is the weighted one.

## What not to claim

Do not claim this snapshot measures literary influence. Hamlet is "like" Macbeth here because both say `haue`. *Paradise Lost* is "like" *Leaves of Grass* because both say `thee`. Those statements are true about **strings in this tokenizer**. They are not claims about Milton and Whitman.
