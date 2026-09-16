# The Gutenberg sample

The files in `gutenberg/` are the 18-book **Project Gutenberg Selections** that shipped with NLTK data when this toy was first written. Each file is one complete work, already lightly packaged for classroom use.

They are public-domain texts. They are not a balanced corpus.

## Inventory

| File | Work | Approx. size | `tf` vocabulary |
| --- | --- | ---: | ---: |
| `austen-emma.txt` | Jane Austen, *Emma* | 887 KB | 9,312 |
| `austen-persuasion.txt` | Jane Austen, *Persuasion* | 466 KB | 5,990 |
| `austen-sense.txt` | Jane Austen, *Sense and Sensibility* | 673 KB | 7,335 |
| `bible-kjv.txt` | King James Bible | 4.3 MB | 16,567 |
| `blake-poems.txt` | William Blake, poems | 38 KB | 1,542 |
| `bryant-stories.txt` | Stories by Bryant | 244 KB | 4,011 |
| `burgess-busterbrown.txt` | Thornton Burgess, *The Adventures of Buster Bear* | 83 KB | 1,568 |
| `carroll-alice.txt` | Lewis Carroll, *Alice's Adventures in Wonderland* | 144 KB | 2,753 |
| `chesterton-ball.txt` | G. K. Chesterton, *The Ball and the Cross* | 457 KB | 8,646 |
| `chesterton-brown.txt` | G. K. Chesterton, Father Brown stories | 407 KB | 8,235 |
| `chesterton-thursday.txt` | G. K. Chesterton, *The Man Who Was Thursday* | 321 KB | 6,524 |
| `edgeworth-parents.txt` | Maria Edgeworth, *The Parent's Assistant* | 917 KB | 9,561 |
| `melville-moby_dick.txt` | Herman Melville, *Moby-Dick* | 1.2 MB | 19,961 |
| `milton-paradise.txt` | John Milton, *Paradise Lost* | 468 KB | 9,321 |
| `shakespeare-caesar.txt` | Shakespeare, *Julius Caesar* (Folio-flavored) | 112 KB | 3,091 |
| `shakespeare-hamlet.txt` | Shakespeare, *Hamlet* | 163 KB | 4,799 |
| `shakespeare-macbeth.txt` | Shakespeare, *Macbeth* | 100 KB | 3,560 |
| `whitman-leaves.txt` | Walt Whitman, *Leaves of Grass* | 711 KB | 14,568 |

Sizes are character counts of the checked-in files. Vocabulary sizes are line counts of the committed `output/tf/` files.

## Why this sample is a good toy

Eighteen documents is small enough that you can open every `tfidf` file and large enough that `idf` is not a coin flip. The books also cluster:

- Three Austen novels share a social lexicon (`mr`, `mrs`, `miss`) and still separate on character names (`emma`, `harriet`, `anne` vs. `elinor`).
- Three Shakespeare plays share Folio spellings (`haue`, `vpon`, `vs`) and still separate on speech prefixes (`macb`, `ham`, `brutus`).
- Three Chesterton books share an authorial voice and still separate on *Thursday*'s `syme`.
- The Bible is an order of magnitude larger than Blake. Length-normalized `tf` is the only reason those two can sit in the same table.

That mix is why the distinctive-term readings in `examples/worked/` look like plot summaries. Character names and setting words have low `df` and high in-document `tf`.

## Why this sample is a bad literary dataset

- **Headers survive.** Alice's first line is `[Alice's Adventures in Wonderland by Lewis Carroll 1865]`. After tokenization that contributes `alices`, `adventures`, `in`, `wonderland`, `by`, `lewis`, `carroll`, and `1865`.
- **The Bible dominates raw counts.** Verse numbers (`1001`, `1002`, …) become unique tokens with `idf = ln(18) ≈ 2.89`.
- **Shakespeare is not modern English.** `haue` is `have`. `macb` is a speech prefix. The ranker cannot know that.
- **No genre balance.** There is no 20th-century prose, no drama besides Shakespeare, no non-English text.
- **NLTK packaging, not Gutenberg etexts.** Line wrapping and the exact header style match the NLTK Gutenberg corpus, not a fresh Project Gutenberg download.

Treat the 18 files as a fixed exam question, not as "English literature."

## Corpus-level vocabulary

From the committed `output/df.txt`:

| Statistic | Value |
| --- | ---: |
| Vocabulary size | 57,368 tokens |
| Tokens with `df = 1` | 36,887 |
| Tokens with `df = 17` | 148 |
| Tokens with `df = 18` (zero IDF) | 221 |

Most strings in the vocabulary never leave the book that introduced them. That is normal for a tiny literary sample with no stemming.

The 221 zero-IDF tokens are listed in [05-quirks-and-design-choices.md](05-quirks-and-design-choices.md). They are the toy's implicit stopword list.
