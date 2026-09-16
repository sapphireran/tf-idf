# Pairwise similarity map

Each book is the sparse TF-IDF vector in `output/tfidf/<file>`.
Similarity is cosine. There are 18 × 17 / 2 = 153 unordered pairs.
This page is the whole map. Reproduce it with:

```bash
python3 examples/reading-companion/cosine_map.py
python3 examples/reading-companion/cosine_map.py --neighbors
```

## What the number is

```
cos(A, B) = (v_A · v_B) / (||v_A|| ||v_B||)
```

Only terms that appear in both files contribute to the dot product.
A name that lives in one novel contributes to that novel's L2 and
then sits unused in every other comparison. That is why name-spiked
books look isolated, and why Folio-spiked plays look like a clique.

## Highest pairs

| Cosine | Pair | Reading |
| ---: | --- | --- |
| 0.3084 | Hamlet ↔ Macbeth | Folio spelling + speech-prefix genre |
| 0.2654 | Milton ↔ Whitman | archaic-pronoun corridor |
| 0.2529 | Caesar ↔ Hamlet | same |
| 0.2261 | Caesar ↔ Macbeth | same |
| 0.2244 | Blake ↔ Milton | corridor |
| 0.2049 | Bible ↔ Milton | corridor |
| 0.1583 | Blake ↔ Whitman | corridor |
| 0.1265 | Melville ↔ Whitman | catalogues, sea, American nouns |
| 0.1189 | Persuasion ↔ Edgeworth | manners / moral-tale diction |
| 0.1138 | Sense ↔ Edgeworth | same |
| 0.1082 | Bible ↔ Whitman | thee / thou / o |
| 0.1009 | Emma ↔ Edgeworth | same manners layer |
| 0.0995 | Father Brown ↔ Edgeworth | late-prose residue |
| 0.0980 | Melville ↔ Milton | thee / thou leak plus elevated nouns |
| 0.0879 | Emma ↔ Persuasion | strongest Austen–Austen pair |
| 0.0879 | Father Brown ↔ Whitman | residue |
| 0.0872 | Bible ↔ Blake | corridor |

The top of the list is two clusters we already named (Folio plays,
pronoun corridor) plus Edgeworth as a manners hub. Nothing else on
the shelf breaks 0.13 except Melville–Whitman.

## Lowest pairs

| Cosine | Pair |
| ---: | --- |
| 0.0002 | Buster Bear ↔ Julius Caesar |
| 0.0004 | Buster Bear ↔ Macbeth |
| 0.0005 | Buster Bear ↔ Hamlet |
| 0.0006 | Alice ↔ Julius Caesar |
| 0.0010 | Emma ↔ Julius Caesar |
| 0.0011 | Thursday ↔ Julius Caesar |

Children's animal names do not overlap Folio tragedy. Alice is
almost as isolated from Caesar. These are not "the most different
books in world literature"; they are the pairs whose surviving
tokens barely intersect after IDF has zeroed the stopwords.

## Nearest neighbor of every book

| Book | 1st neighbor | Cos | 2nd neighbor | Cos |
| --- | --- | ---: | --- | ---: |
| Emma | Edgeworth | 0.1009 | Persuasion | 0.0879 |
| Persuasion | Edgeworth | 0.1189 | Emma | 0.0879 |
| Sense | Edgeworth | 0.1138 | Persuasion | 0.0676 |
| KJV | Milton | 0.2049 | Whitman | 0.1082 |
| Blake | Milton | 0.2244 | Whitman | 0.1583 |
| Bryant | Whitman | 0.0844 | Father Brown | 0.0768 |
| Buster Bear | Bryant | 0.0294 | Father Brown | 0.0254 |
| Alice | Father Brown | 0.0302 | Edgeworth | 0.0301 |
| Ball and Cross | Father Brown | 0.0523 | Whitman | 0.0378 |
| Father Brown | Edgeworth | 0.0995 | Whitman | 0.0879 |
| Thursday | Father Brown | 0.0510 | Whitman | 0.0329 |
| Edgeworth | Persuasion | 0.1189 | Sense | 0.1138 |
| Moby-Dick | Whitman | 0.1265 | Milton | 0.0980 |
| Paradise Lost | Whitman | 0.2654 | Blake | 0.2244 |
| Julius Caesar | Hamlet | 0.2529 | Macbeth | 0.2261 |
| Hamlet | Macbeth | 0.3084 | Caesar | 0.2529 |
| Macbeth | Hamlet | 0.3084 | Caesar | 0.2261 |
| Leaves of Grass | Milton | 0.2654 | Blake | 0.1583 |

Islands: Alice (best friend 0.030) and Buster Bear (0.029). Their
vocabularies are private. Hubs: Edgeworth (manners), Milton/Whitman
(address), Hamlet (Folio).

## Author-group means

| Group | Intra-group mean cosine |
| --- | ---: |
| Shakespeare (3 plays) | 0.2625 |
| Austen (3 novels) | 0.0743 |
| Chesterton (3 books) | 0.0418 |

Author is a good cluster only when the files share a *non-name*
private alphabet. Folio spelling qualifies. Cast lists do not.

## Compact matrix

Values rounded to two decimals. `au-` Austen, `ch-` Chesterton,
`sh-` Shakespeare.

|  | emma | pers | sens | kjv | blak | brya | bust | alic | ball | brow | thur | edge | moby | milt | caes | haml | macb | whit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| emma | — | .09 | .07 | .01 | .01 | .02 | .01 | .01 | .02 | .05 | .01 | .10 | .02 | .02 | .00 | .00 | .00 | .03 |
| pers | .09 | — | .07 | .01 | .01 | .03 | .01 | .01 | .02 | .06 | .01 | .12 | .04 | .03 | .00 | .00 | .00 | .04 |
| sens | .07 | .07 | — | .01 | .01 | .02 | .00 | .01 | .01 | .04 | .01 | .11 | .02 | .02 | .00 | .00 | .00 | .03 |
| kjv | .01 | .01 | .01 | — | .09 | .07 | .00 | .01 | .01 | .03 | .01 | .03 | .05 | .20 | .02 | .03 | .03 | .11 |
| blak | .01 | .01 | .01 | .09 | — | .05 | .01 | .01 | .01 | .03 | .01 | .04 | .04 | .22 | .02 | .02 | .02 | .16 |
| brya | .02 | .03 | .02 | .07 | .05 | — | .03 | .03 | .03 | .08 | .02 | .07 | .06 | .07 | .00 | .01 | .01 | .08 |
| bust | .01 | .01 | .00 | .00 | .01 | .03 | — | .01 | .01 | .03 | .01 | .02 | .01 | .01 | .00 | .00 | .00 | .01 |
| alic | .01 | .01 | .01 | .01 | .01 | .03 | .01 | — | .01 | .03 | .01 | .03 | .02 | .01 | .00 | .00 | .00 | .02 |
| ball | .02 | .02 | .01 | .01 | .01 | .03 | .01 | .01 | — | .05 | .02 | .03 | .02 | .03 | .00 | .00 | .00 | .04 |
| brow | .05 | .06 | .04 | .03 | .03 | .08 | .03 | .03 | .05 | — | .05 | .10 | .07 | .06 | .00 | .01 | .00 | .09 |
| thur | .01 | .01 | .01 | .01 | .01 | .02 | .01 | .01 | .02 | .05 | — | .03 | .02 | .02 | .00 | .00 | .00 | .03 |
| edge | .10 | .12 | .11 | .03 | .04 | .07 | .02 | .03 | .03 | .10 | .03 | — | .05 | .05 | .00 | .01 | .01 | .06 |
| moby | .02 | .04 | .02 | .05 | .04 | .06 | .01 | .02 | .02 | .07 | .02 | .05 | — | .10 | .01 | .01 | .01 | .13 |
| milt | .02 | .03 | .02 | .20 | .22 | .07 | .01 | .01 | .03 | .06 | .02 | .05 | .10 | — | .04 | .06 | .06 | .27 |
| caes | .00 | .00 | .00 | .02 | .02 | .00 | .00 | .00 | .00 | .00 | .00 | .00 | .01 | .04 | — | .25 | .23 | .03 |
| haml | .00 | .00 | .00 | .03 | .02 | .01 | .00 | .00 | .00 | .01 | .00 | .01 | .01 | .06 | .25 | — | .31 | .03 |
| macb | .00 | .00 | .00 | .03 | .02 | .01 | .00 | .00 | .00 | .00 | .00 | .01 | .01 | .06 | .23 | .31 | — | .03 |
| whit | .03 | .04 | .03 | .11 | .16 | .08 | .01 | .02 | .04 | .09 | .03 | .06 | .13 | .27 | .03 | .03 | .03 | — |

Read down the Shakespeare block in the lower right: that 3×3 is the
only author-shaped square on the page. The Milton/Whitman/Blake/KJV
block in the middle-right is the corridor. The top-left Austen
square is paler than the Austen–Edgeworth column.
