# The 18-book Gutenberg corpus

`gutenberg/` holds 18 public-domain texts that NLTK's Gutenberg sample
also made famous. They are a decent TF-IDF demo because they mix:

- three Austen novels (overlapping diction, different casts)
- three Shakespeare plays (overlapping Early Modern English, different
  speaker tags)
- three Chesterton books (same author, different protagonists)
- several one-off titles that should be easy to fingerprint (`Alice`,
  *Moby-Dick*, Burgess's Buster Bear, the King James Bible)

Each file starts with a one-line title banner in square brackets, then
the body. The tokenizer treats that banner as ordinary words, which is
usually harmless (`macbeth`, `alice`) and occasionally informative
(`gutenberg` leftovers in a couple of files).

## Inventory

| File | Work | Rough size |
| --- | --- | ---: |
| `austen-emma.txt` | Jane Austen, *Emma* | long novel |
| `austen-persuasion.txt` | Jane Austen, *Persuasion* | novel |
| `austen-sense.txt` | Jane Austen, *Sense and Sensibility* | novel |
| `bible-kjv.txt` | King James Bible | very long |
| `blake-poems.txt` | William Blake, *Songs of Innocence and of Experience* plus *The Book of Thel* | verse, short |
| `bryant-stories.txt` | stories collected under Bryant | children's / folk |
| `burgess-busterbrown.txt` | Thornton W. Burgess, *The Adventures of Buster Bear* | short children's book |
| `carroll-alice.txt` | Lewis Carroll, *Alice's Adventures in Wonderland* | novella |
| `chesterton-ball.txt` | G.K. Chesterton, *The Ball and the Cross* | novel |
| `chesterton-brown.txt` | G.K. Chesterton, Father Brown stories | story collection |
| `chesterton-thursday.txt` | G.K. Chesterton, *The Man Who Was Thursday* | novel |
| `edgeworth-parents.txt` | Maria Edgeworth, *The Parent's Assistant* | stories |
| `melville-moby_dick.txt` | Herman Melville, *Moby-Dick* | long novel |
| `milton-paradise.txt` | John Milton, *Paradise Lost* | epic verse |
| `shakespeare-caesar.txt` | Shakespeare, *Julius Caesar* (First Folio spelling) | play |
| `shakespeare-hamlet.txt` | Shakespeare, *Hamlet* (First Folio spelling) | play |
| `shakespeare-macbeth.txt` | Shakespeare, *Macbeth* (First Folio spelling) | play |
| `whitman-leaves.txt` | Walt Whitman, *Leaves of Grass* | verse |

Eighteen files is large enough that IDF is meaningful (`ln(18/1) ≈
2.89`, `ln(18/18) = 0`) and small enough that you can still name every
document.

## Why this mix is pedagogically useful

**Same author, different books.** Austen shares `mr`, `mrs`, `said`.
IDF therefore suppresses those, and the leftover top terms are the
casts: Emma Woodhouse versus Anne Elliot versus Elinor Dashwood.
Chesterton splits the same way (`syme` vs `turnbull` vs `flambeau`).

**Same genre, different identifiers.** The three plays share `haue`,
`vs`, `thee`. IDF only partly suppresses them, because they are still
rarer in the novels. Unique speaker prefixes (`macb`, `ham`, `bru`)
become the loudest signal. That is a feature if you want to know
"which file is this?" and a bug if you wanted "what is the play
about?"

**One extreme outlier.** *The Adventures of Buster Bear* is short and
repeats `Buster` constantly. `buster` lands at `0.040354`, the largest
head term in `output/tfidf/`. TF-IDF is doing the right thing: high TF
in a short document, df = 1.

**Verse versus prose.** Blake, Milton, and Whitman use `thee` / `thou`
/ `o`. Those pronouns survive IDF because most of the novels do not
use them. Content words have to fight function words that happen to be
collection-rare.

## What is not in the folder

- no metadata sidecar (language, year, genre)
- no gold keywords
- no train/test split; this is not a classification dataset
- no license file beyond whatever banner the Gutenberg excerpt kept

The files are teaching data for a term-weighting example, not a
repackaged Gutenberg mirror. If you want the full catalog, go to
Project Gutenberg itself.

## Pairing with the tiny corpus

If you want to *see* every token, do not start here. Start with
`examples/tiny-corpus/` (five original paragraphs) or
`examples/classic-three-docs/` (three sentences). Come back to
`gutenberg/` once the formula is boring.
