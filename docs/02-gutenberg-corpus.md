# Gutenberg shelf

Eighteen public-domain texts sit in `gutenberg/`. They were chosen as a
mixed personal reading pile — novels, plays, poems, a children's book, and
the King James Bible — so IDF has something to push against. A word that
is ordinary in Austen can still be distinctive if the rest of the shelf is
whaling, prophecy, and blank verse.

Hidden files (`.DS_Store`) are skipped by the Perl `if ($f !~ /^\./)`
guard. They are not part of `N = 18`.

## Inventory

Lengths are line counts of the checked-in files, not token counts.

| File | Work | Lines | Tokens that rise to the top |
| --- | --- | --- | --- |
| `austen-emma.txt` | Jane Austen, *Emma* | 16,823 | `emma`, `harriet`, `weston`, `knightley` |
| `austen-persuasion.txt` | Jane Austen, *Persuasion* | 8,471 | `elliot`, `wentworth`, `anne`, `musgrove`, `uppercross` |
| `austen-sense.txt` | Jane Austen, *Sense and Sensibility* | 14,796 | `elinor`, `marianne`, `dashwood`, `jennings`, `willoughby` |
| `bible-kjv.txt` | King James Bible | 99,805 | `unto`, `israel`, `saith`, `thee` |
| `blake-poems.txt` | William Blake, *Songs* and related poems | 1,441 | `thel`, `weep`, `lyca`, `vales` |
| `bryant-stories.txt` | Stories by Sara Cone Bryant | 5,538 | `margery`, `jackal`, `brahmin`, `epaminondas` |
| `burgess-busterbrown.txt` | Thornton Burgess, *The Adventures of Buster Bear* | 1,671 | `buster` 0.0404 (df = 1), then `browns`, `joe`, `blacky` |
| `carroll-alice.txt` | Lewis Carroll, *Alice's Adventures in Wonderland* | 3,331 | `alice`, `gryphon`, `dormouse`, `duchess` |
| `chesterton-ball.txt` | G. K. Chesterton, *The Ball and the Cross* | 9,548 | `turnbull`, `macian`, `evan` |
| `chesterton-brown.txt` | Chesterton, Father Brown stories | 7,654 | `flambeau`, `boulnois`, `muscari`, `brown` |
| `chesterton-thursday.txt` | Chesterton, *The Man Who Was Thursday* | 6,793 | `syme`, `gregory`, `professor`, `gogol` |
| `edgeworth-parents.txt` | Maria Edgeworth, *The Parent's Assistant* | 18,297 | `cecilia`, `susan`, `piedro`, `leonora` |
| `melville-moby_dick.txt` | Herman Melville, *Moby-Dick* | 22,924 | `whale`, `ahab`, `sperm`, `stubb`, `queequeg` |
| `milton-paradise.txt` | John Milton, *Paradise Lost* | 10,635 | `heaven`, `eve`, `adam` (plus `thee`/`thou`) |
| `shakespeare-caesar.txt` | *Julius Caesar* | 3,523 | `bru`, `brutus`, `cassi`, `cassius`, `caes` |
| `shakespeare-hamlet.txt` | *Hamlet* | 4,922 | `ham`, `haue`, `hor`, `hamlet` |
| `shakespeare-macbeth.txt` | *Macbeth* | 3,286 | `macb`, `haue`, `macbeth`, `banquo` |
| `whitman-leaves.txt` | Walt Whitman, *Leaves of Grass* | 17,435 | `o`, `thee`, `poems`, `pioneers`, `chant` |

The Bible is more than four times the length of *Moby-Dick* and about seventy
times Blake. Normalized TF is what keeps `unto` from being an accident of
file size: it is a large *fraction* of the KJV token stream, and it is rarer
on a shelf of 19th-century novels than `the`.

## Distinctive terms from the checked-in tables

These are the actual top weights in `output/tfidf/`, not a guessed keyword
list. Speaker abbreviations in the play texts are tokens like any other.

**Alice** — `alice 0.025957`, `gryphon 0.004547`, `dormouse 0.004242`,
`duchess 0.004242`, `hatter 0.003708`. The title character has both high TF
and a modest IDF (`df = 3`: Carroll, *Thursday*, and Edgeworth all say
"Alice"). Creature names are rarer and still cannot catch up to the sheer
number of times the book says `alice`.

**Moby-Dick** — `whale 0.004943`, `ahab 0.004322`, `sperm 0.003258`,
`stubb 0.003095`, `queequeg 0.002877`. `whale` appears in six books, so its
IDF is only `ln(18/6) ≈ 1.099`. It still wins because the TF is enormous.
`pequod` is unique (`df = 1`) but used less often, so it lands further down
(`0.001650`).

**Hamlet** — `ham 0.014075` beats `hamlet 0.003582`. The quarto/folio-style
speaker prefix `HAM.` tokenizes to `ham`. The same thing happens in Macbeth
with `macb` (0.021556) versus `macbeth` (0.009755). Early-modern spelling
(`haue`, `selfe`, `loue`, `vs`, `giue`) also ranks because those forms are
concentrated in the three play files.

**Emma** — `emma 0.010432`, then the Highbury circle: `harriet`, `weston`,
`knightley`, `elton`, `fairfax`, `woodhouse`. `mr` and `mrs` score because
Austen uses them constantly and the rest of the shelf does not (Melville
and the Bible prefer other honorifics and titles).

**KJV** — `unto`, `israel`, `saith`, `thee`, `david`. Function words that
look "stopword-like" in modern English are collection-specific here. `unto`
is ordinary scripture and unusual Austen.

**Blake** — short file, so a handful of repeated poem-words (`thel`, `weep`,
`lyca`) get a large TF. `tyger` never appears because the checked-in text
does not contain that spelling as a standalone token.

**Buster Bear** — `buster` at 0.0404 is the heaviest single weight on the
shelf. The file is short, the name is unique (`df = 1`), and Burgess
repeats it constantly. Animal sidekicks (`blacky`, `billy`, `chatterer`)
fill the rest of the head.

**Chesterton** — each book is dominated by its own surnames: `turnbull` /
`macian` in *The Ball and the Cross*, `flambeau` in Father Brown, `syme`
in *Thursday*. That is TF-IDF doing collection-internal contrast: the
three Chesterton files do not share enough rare vocabulary to cancel
those names.

**Caesar** — same speaker-tag pattern as Hamlet/Macbeth. `bru` (0.0208)
and `cassi` (0.0146) outrank `caesar` (0.0073), and `caes` is a separate
token. `caesar` itself has `df = 8`, so IDF is only `ln(18/8) ≈ 0.811`.

## Why this shelf is a good TF-IDF demo

1. **Shared function words.** `the` and `and` occur in all 18 files, IDF 0.
   The tables show those words being present and then disappearing from the
   ranking, which is the whole point of IDF.
2. **Overlapping names.** `alice`, `emma`, `caesar`, and `hamlet` leak into
   other books as quotations or ordinary given names. IDF records the leak
   instead of pretending each name is unique.
3. **Wildly different lengths.** Normalization is visible: Blake can still
   have competitive top scores.
4. **Orthography as signal.** Shakespeare files are a reminder that "the
   same word" is a tokenizer decision, not a linguistic fact.

A query that uses the distinctive terms above will recover the expected
book. That experiment is written out in
[06-querying-and-ranking.md](06-querying-and-ranking.md).
