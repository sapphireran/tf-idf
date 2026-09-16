# Three Austen novels, one IDF table

*Emma*, *Persuasion*, and *Sense and Sensibility* share an author, a period,
and a lot of drawing-room English. Character names barely overlap. That is a
clean demonstration of what this repo’s TF-IDF actually rewards.

IDF values are corpus-wide (`N = 18`), not “Austen-only.” A word that is
ordinary in these three novels can still get a healthy IDF if Blake, the KJV,
and the plays never use it.

## Top names side by side

| *Emma* | *Persuasion* | *Sense and Sensibility* |
| --- | --- | --- |
| emma 0.01043 | elliot 0.00881 | elinor 0.01503 |
| harriet 0.00713 | wentworth 0.00663 | marianne 0.00906 |
| weston 0.00698 | anne 0.00587 | dashwood 0.00545 |
| knightley 0.00614 | musgrove 0.00385 | jennings 0.00494 |
| elton 0.00579 | russell 0.00311 | willoughby 0.00325 |

No heroine’s given name is the #1 term in more than one column. The metric is
doing document separation, not “detect Austen.”

## Cross-file scores for the same string

Values are TF-IDF in that novel, or `—` if the term never occurs there.

| Term | df | idf ≈ | *Emma* | *Persuasion* | *Sense* |
| --- | ---: | ---: | ---: | ---: | ---: |
| `emma` | 2 | 2.197 | **0.01043** | 0.000026 | — |
| `harriet` | 1 | 2.890 | **0.00713** | — | — |
| `knightley` | 1 | 2.890 | **0.00614** | — | — |
| `elinor` | 1 | 2.890 | — | — | **0.01503** |
| `marianne` | 2 | 2.197 | — | — | **0.00906** |
| `dashwood` | 1 | 2.890 | — | — | **0.00545** |
| `elliot` | 1 | 2.890 | — | **0.00881** | — |
| `wentworth` | 1 | 2.890 | — | **0.00663** | — |
| `anne` | 6 | 1.099 | 0.000014 | **0.00587** | 0.000055 |
| `jane` | 3 | 1.792 | **0.00308** | 0.000022 | 0.000015 |
| `mr` | 10 | 0.588 | 0.00418 | 0.00180 | 0.00088 |
| `mrs` | 8 | 0.811 | 0.00352 | 0.00283 | 0.00359 |

Read this as three different effects stacked on the same formula.

### 1. Exclusive names get the full singleton IDF

`harriet`, `knightley`, `elinor`, `dashwood`, `elliot`, `wentworth` appear in
exactly one of the 18 Gutenberg files. Their IDF is `ln(18) ≈ 2.890`. Whoever
is mentioned more often inside that novel wins.

### 2. A name that leaks into another file is taxed

`emma` also occurs in *Persuasion* (`df = 2`), so the heroine of *Emma* pays
the `ln(9) ≈ 2.197` rate. She still ranks first in her own book because the
raw TF is large, and she is a rounding error in *Persuasion*.

`marianne` leaks into Edgeworth, same tax.

`woodhouse` leaks into *Moby-Dick* of all places (`df = 2`). Emma’s family
name therefore does not get singleton IDF. It still ranks in *Emma* (8th)
because the household is named often.

### 3. Common given names are the worst of both worlds

`anne` is the center of *Persuasion* but `df = 6` (Chesterton, *Sense*,
Edgeworth, …). IDF drops to `ln(3) ≈ 1.099`. Wentworth and Elliot, who are
less famous as English given names, overtake her.

`jane` appears in all three Austen novels (`df = 3`): Jane Fairfax in *Emma*,
plus lighter mentions elsewhere. It is a useful *Emma* signal and almost
useless in the other two.

## Why `mr` and `mrs` still rank

They are not rare. They are **unevenly distributed in this sample**. Ten
files say `mr`; eight say `mrs`. Plays, the KJV, Blake, and Whitman do not
use those honorifics the way a novel of manners does, so IDF stays positive.

Inside Austen, `mrs` is actually a stronger *shared* novelistic feature than
any plot word: it ranks 5th–9th in all three files. If you wanted “terms that
mean Austen-ish,” you would look at the intersection of high-TF terms with
medium DF, not at the top of a single TF-IDF list. This pipeline does not
emit that intersection; it emits per-document products.

## Function words that do vanish

`a`, `and`, `the`, `to`, `of`, `in`, `that` have `df = 18` and TF-IDF `0` in
every Austen file. *Emma* has 221 such zeros — the vocabulary that every
Gutenberg file in the sample happened to use at least once.

That list includes some non-stopwords (`angry`, `bed`, `breath`). Zero here
means “not a distinguishing feature of *Emma* **against these 17 other
files**,” not “unimportant in the novel.”

## Places and titles

| Term | Novel it characterizes | Note |
| --- | --- | --- |
| `hartfield` | *Emma* | house name, singleton |
| `kellynch`, `uppercross`, `lyme` | *Persuasion* | setting nouns |
| `barton` | *Sense* | Barton cottage |
| `captain` | *Persuasion* | Wentworth’s rank; mid IDF, high TF |

Setting words behave like surnames when the place is invented. Real-world
words (`lyme`, `captain`) compete with other books and need more repetition
to stay visible.

## Tiny-corpus analogue

`apple` vs `orchard` in [`hand-calculation.md`](hand-calculation.md) is the
same picture as `anne` vs `elliot`: equal or greater in-document attention
cannot beat a worse DF. Austen just does it with 80,000–160,000 tokens
instead of 20.

## Command

```bash
python3 examples/rank_top_terms.py --dir output/tfidf --file austen-emma.txt --k 12
python3 examples/rank_top_terms.py --dir output/tfidf --file austen-persuasion.txt --k 12
python3 examples/rank_top_terms.py --dir output/tfidf --file austen-sense.txt --k 12
```

Term-level DF: [`../docs/idf-selected-terms.md`](../docs/idf-selected-terms.md).
