# Gutenberg collection

The experiment treats each file in `gutenberg/` as one document. Hidden files (`.DS_Store`) are ignored. That leaves **18 documents**.

Token and type counts below were produced with the same cleaning rules as `tf-idf-values.pl` (lowercase, strip non-alphanumerics, split on spaces). They will not match `wc -w` on the raw files.

## Inventory

| file | work (plain-text Gutenberg edition) | tokens | types |
| --- | --- | --- | --- |
| `austen-emma.txt` | Jane Austen, *Emma* | 158,131 | 9,312 |
| `austen-persuasion.txt` | Jane Austen, *Persuasion* | 83,303 | 5,990 |
| `austen-sense.txt` | Jane Austen, *Sense and Sensibility* | 118,673 | 7,335 |
| `bible-kjv.txt` | King James Bible | 821,131 | 16,567 |
| `blake-poems.txt` | William Blake, poems (incl. *Thel*, *Songs*) | 6,819 | 1,542 |
| `bryant-stories.txt` | Stories by Sara Cone Bryant | 45,973 | 4,011 |
| `burgess-busterbrown.txt` | Thornton Burgess, *Adventures of Buster Bear* (and related Brown-family stories in this dump) | 15,870 | 1,568 |
| `carroll-alice.txt` | Lewis Carroll, *Alice's Adventures in Wonderland* (1865) | 26,383 | 2,753 |
| `chesterton-ball.txt` | G. K. Chesterton, *The Ball and the Cross* | 81,576 | 8,646 |
| `chesterton-brown.txt` | Chesterton, Father Brown stories | 71,626 | 8,235 |
| `chesterton-thursday.txt` | Chesterton, *The Man Who Was Thursday* | 57,915 | 6,524 |
| `edgeworth-parents.txt` | Maria Edgeworth, *The Parent's Assistant* | 166,012 | 9,561 |
| `melville-moby_dick.txt` | Herman Melville, *Moby-Dick* | 212,013 | 19,961 |
| `milton-paradise.txt` | John Milton, *Paradise Lost* | 79,649 | 9,321 |
| `shakespeare-caesar.txt` | Shakespeare, *Julius Caesar* | 20,451 | 3,091 |
| `shakespeare-hamlet.txt` | Shakespeare, *Hamlet* | 29,579 | 4,799 |
| `shakespeare-macbeth.txt` | Shakespeare, *Macbeth* | 17,722 | 3,560 |
| `whitman-leaves.txt` | Walt Whitman, *Leaves of Grass* | 121,688 | 14,568 |

Totals are approximate at the token level (~2.13 million tokens, ~57k collection-wide types after union). `output/idf.txt` has 57,368 terms, which is that union plus whatever digit-strings and leftovers survived cleaning.

## Why this mix is a good TF-IDF teaching set

The collection is **small enough to run in Perl on a laptop** and **heterogeneous enough that IDF does real work**:

- **Three Austen novels** share period English, drawing-room vocabulary, and the honorifics `mr` / `mrs`. Those words get a middling IDF. Character names still lead *Emma* (`emma` itself also appears in *Persuasion*, so `df = 2`) because in-book TF stays high.
- **Three Shakespeare plays** share Early Modern spelling (`haue`, `vpon`, `selfe`). Those forms are rare in the novels, so they rank high in every play — a reminder that IDF measures rarity *in this collection*, not "importance in English."
- **Three Chesterton books** share an authorial voice. *Thursday* still surfaces `syme` and `gregory`; the overlap does not erase plot-specific names.
- **One very long sacred text** (KJV) and **one very long novel** (Moby-Dick) stress length normalization. Raw counts would make `the` in the Bible dwarf everything else.
- **Short verse** (Blake) has a tiny token count. A single repetition of `thel` or `lyca` is enough to lead that file's TF-IDF list.

If every document were another Austen novel, `mr` would look like a stopword and you would learn less from the ranking.

## Distinctive terms (preview)

These are the TF-IDF heads after discarding the obvious speech-prefix abbreviations. Full tables: [interpreting-results.md](interpreting-results.md).

| file | distinctive terms (selected) |
| --- | --- |
| `carroll-alice.txt` | alice, gryphon, duchess, dormouse, hatter, caterpillar |
| `melville-moby_dick.txt` | whale, ahab, sperm, stubb, queequeg, starbuck, pequod |
| `austen-emma.txt` | emma, harriet, weston, knightley, elton, hartfield |
| `chesterton-thursday.txt` | syme, gregory, professor, marquis, gogol |
| `milton-paradise.txt` | eve, adam, satan, sovran, paradise, angelick |
| `bible-kjv.txt` | unto, israel, saith, david, judah, jesus, moses |
| `whitman-leaves.txt` | pioneers, manhattan, eidolons, chants, america |
| `blake-poems.txt` | thel, lyca, weep, lamb, infant |
| `burgess-busterbrown.txt` | buster, blacky, chatterer, otter, sammy |

## File naming

Names are `author-shorttitle.txt` in ASCII, underscore only in `moby_dick`. The Perl scripts use the filename as the document id in `df.txt`, so renaming a book changes every DF row that lists it and would require a rerun.

## What is not in the collection

- No modern copyrighted novels.
- No web pages, tweets, or HTML.
- No parallel translations of the same work (which would collapse IDF for plot words).
- No duplicate Alice / extra Shakespeare folio to pad `N`.

Adding a nineteenth file is a useful experiment: copy `carroll-alice.txt` to `carroll-alice-copy.txt` and rerun. `alice` already has `df = 3`; the copy would make `df = 4` and IDF would fall from `ln(18/3)` to `ln(19/4)` (or `ln(18/4)` if you forget to recount `N`). That single change is the fastest way to feel what "inverse document frequency" means.

## Provenance

These files were already in the repository when the notes were expanded. They are Project Gutenberg-style plain text (title lines such as `[Alice's Adventures in Wonderland by Lewis Carroll 1865]`). Some still carry catalog residue; tokenization will turn those into extra terms. Do not "clean" them in place if you want the committed `output/` tables to stay reproducible.
