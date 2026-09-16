# Gutenberg top TF-IDF terms

Rankings below come from the checked-in `output/tfidf/` tables, sorted
numerically:

```bash
python3 examples/rank_top_terms.py --dir output/tfidf --k 12
```

`idf(t) = ln(18 / df(t))`. A term that appears in every file scores `0` and
never makes these lists. Peak magnitudes are **not** comparable across books
of different lengths; read each block as “what is distinctive *inside this
file*.”

## Jane Austen — *Emma*

| Rank | Term | TF-IDF |
| ---: | --- | ---: |
| 1 | `emma` | 0.010432 |
| 2 | `harriet` | 0.007127 |
| 3 | `weston` | 0.006980 |
| 4 | `knightley` | 0.006140 |
| 5 | `elton` | 0.005793 |
| 6 | `mr` | 0.004177 |
| 7 | `fairfax` | 0.003673 |
| 8 | `woodhouse` | 0.003653 |
| 9 | `mrs` | 0.003522 |
| 10 | `jane` | 0.003081 |
| 11 | `hartfield` | 0.002796 |
| 12 | `churchill` | 0.002625 |

The novel is named after the heroine and then talks about her circle. `emma`
has `df = 2` (a passing mention in *Persuasion*); `harriet` / `knightley` /
`elton` are singletons. `mr` and `mrs` survive because they are absent from
several non-novel files, not because they are rare English words. Full
write-up: [`compare-austen-novels.md`](compare-austen-novels.md).

## Jane Austen — *Persuasion*

| Rank | Term | TF-IDF |
| ---: | --- | ---: |
| 1 | `elliot` | 0.008813 |
| 2 | `wentworth` | 0.006627 |
| 3 | `anne` | 0.005868 |
| 4 | `musgrove` | 0.003851 |
| 5 | `russell` | 0.003112 |
| 6 | `mrs` | 0.002833 |
| 7 | `charles` | 0.002762 |
| 8 | `uppercross` | 0.002672 |
| 9 | `kellynch` | 0.002533 |
| 10 | `captain` | 0.002521 |
| 11 | `lyme` | 0.002325 |
| 12 | `benwick` | 0.002290 |

Anne Elliot should theoretically dominate, but `anne` has `df = 6` in this
sample. The family name `elliot` and the suitor `wentworth` are singletons
and overtake her.

## Jane Austen — *Sense and Sensibility*

| Rank | Term | TF-IDF |
| ---: | --- | ---: |
| 1 | `elinor` | 0.015032 |
| 2 | `marianne` | 0.009061 |
| 3 | `dashwood` | 0.005449 |
| 4 | `jennings` | 0.004938 |
| 5 | `mrs` | 0.003590 |
| 6 | `willoughby` | 0.003254 |
| 7 | `lucy` | 0.002903 |
| 8 | `brandon` | 0.002822 |
| 9 | `ferrars` | 0.002651 |
| 10 | `barton` | 0.002165 |
| 11 | `edward` | 0.001942 |
| 12 | `middleton` | 0.001609 |

`elinor` is a singleton and is said constantly; she posts the largest peak
of the three Austen files. `marianne` is slightly diluted (`df = 2`, also
Edgeworth).

## Herman Melville — *Moby-Dick*

| Rank | Term | TF-IDF |
| ---: | --- | ---: |
| 1 | `whale` | 0.004943 |
| 2 | `ahab` | 0.004322 |
| 3 | `sperm` | 0.003258 |
| 4 | `stubb` | 0.003095 |
| 5 | `queequeg` | 0.002877 |
| 6 | `whales` | 0.002760 |
| 7 | `starbuck` | 0.002304 |
| 8 | `pequod` | 0.001650 |
| 9 | `nantucket` | 0.001295 |
| 10 | `boats` | 0.001270 |
| 11 | `whaling` | 0.001171 |
| 12 | `moby` | 0.001077 |

`whale` is the topical word but `df = 6`. `ahab` is `df = 2` (King James
Ahab). The captain almost catches the animal. Ishmael, the narrator, barely
registers (`tfidf ≈ 0.000187`) because he is named sparingly **and** shares
the biblical `df = 2`. The book’s most famous first line is a TF-IDF
non-event.

## Lewis Carroll — *Alice's Adventures in Wonderland*

| Rank | Term | TF-IDF |
| ---: | --- | ---: |
| 1 | `alice` | 0.025957 |
| 2 | `gryphon` | 0.004547 |
| 3 | `dormouse` | 0.004242 |
| 4 | `duchess` | 0.004242 |
| 5 | `hatter` | 0.003708 |
| 6 | `turtle` | 0.003169 |
| 7 | `caterpillar` | 0.001820 |
| 8 | `rabbit` | 0.001778 |
| 9 | `alices` | 0.001305 |
| 10 | `herself` | 0.001266 |
| 11 | `soup` | 0.001214 |
| 12 | `mouse` | 0.001160 |

`alice` is a short-book, high-repetition name (`df = 3`). `alices` is the
tokenizer gluing `Alice's`. `herself` ranking at all is the un-stopped
pronoun problem; IDF is not a complete stop list.

## William Blake — poems

| Rank | Term | TF-IDF |
| ---: | --- | ---: |
| 1 | `thel` | 0.005581 |
| 2 | `weep` | 0.003957 |
| 3 | `lyca` | 0.002976 |
| 4 | `thee` | 0.002662 |
| 5 | `vales` | 0.001742 |
| 6 | `oer` | 0.001697 |
| 7 | `har` | 0.001488 |
| 8 | `thou` | 0.001466 |
| 9 | `lamb` | 0.001461 |
| 10 | `weeping` | 0.001461 |
| 11 | `infant` | 0.001459 |
| 12 | `morn` | 0.001319 |

*The Book of Thel* and “The Little Girl Lost” donate the proper names.
`oer` is `o'er` after the apostrophe is deleted. `thee` / `thou` persist
because they miss some of the modern prose files.

## Thornton Burgess — Buster Bear (filename: `burgess-busterbrown.txt`)

| Rank | Term | TF-IDF |
| ---: | --- | ---: |
| 1 | `buster` | 0.040354 |
| 2 | `browns` | 0.010930 |
| 3 | `joe` | 0.010216 |
| 4 | `blacky` | 0.009270 |
| 5 | `billy` | 0.007089 |
| 6 | `otter` | 0.005634 |
| 7 | `sammy` | 0.005389 |
| 8 | `chatterer` | 0.005271 |
| 9 | `trout` | 0.005113 |
| 10 | `mink` | 0.005090 |
| 11 | `jay` | 0.004544 |
| 12 | `farmer` | 0.004359 |

Shortest-but-one file in the sample, and the prose says `buster` on almost
every page. This is the ceiling of raw relative TF × singleton IDF in the
collection. The filename’s “Buster Brown” is a misnomer; the list is forest
animals.

## G. K. Chesterton

**The Ball and the Cross** — `turnbull`, `macian`, `evan`, then `ebook` and
`gutenberg`. Those last two are leftover Project Gutenberg boilerplate that
no other file in the sample kept, so they get `df = 1`.

**Father Brown** — `flambeau` first, then one-story surnames (`boulnois`,
`muscari`, `fanshaw`). The priest’s own surname `brown` is common English
and only ranks mid-list.

**The Man Who Was Thursday** — `syme` at 0.024, then `gregory`, `professor`,
`marquis`, `anarchists`. A single invented surname plus a conspiracy
vocabulary.

## King James Bible

| Rank | Term | TF-IDF |
| ---: | --- | ---: |
| 1 | `unto` | 0.012037 |
| 2 | `israel` | 0.004001 |
| 3 | `saith` | 0.003377 |
| 4 | `thee` | 0.002295 |
| 5 | `david` | 0.002206 |
| 6 | `judah` | 0.002173 |
| 7 | `thou` | 0.002169 |
| 8 | `hath` | 0.001911 |
| 9 | `lord` | 0.001739 |
| 10 | `jesus` | 0.001533 |
| 11 | `thereof` | 0.001413 |
| 12 | `thy` | 0.001408 |

Not “God” or “said.” The distinctive layer is **translation dialect** that
only some of the literary files borrow. `lord` is frequent but more widely
shared, so it sits below `unto`.

## John Milton — *Paradise Lost*

`thee`, `thou`, `heaven`, `thy`, `eve`, `th`, `adam`, `hath`, `spake`,
`satan`. Epic pronouns and a clipped `th` (from `th'` elisions after the
apostrophe is stripped) outrank the proper names because Adam / Eve / Satan
also live in the KJV and in later prose (`df = 7`).

## Walt Whitman — *Leaves of Grass*

`o`, `thee`, `poems`, `pioneers`, `states`, `passd`, `chant`, `cities`,
`forever`, `soul`, `manhattan`. The vocative `O` is a stylistic fingerprint.
`passd` is `pass'd`. Geography (`states`, `manhattan`) is the content signal.

## Shakespeare

Speech prefixes occupy the top slots. That is a separate example:
[`shakespeare-speaker-tags.md`](shakespeare-speaker-tags.md).

## Sara Cone Bryant and Maria Edgeworth

Story-collection behavior: each tale donates a different name (`margery`,
`jackal`, `epaminondas`, `cecilia`, `piedro`), so no single term reaches
Austen- or Burgess-level peaks. TF-IDF still lists *someone*; it just cannot
summarize an anthology with one word.

## How to regenerate a block

```bash
python3 examples/rank_top_terms.py --dir output/tfidf --file melville-moby_dick.txt --k 12
```

If you recompute IDF with a different `N`, every column in this page moves.
Quote the checked-in tables unless you also update the docs.
