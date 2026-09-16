# Gutenberg sample corpus

`gutenberg/` is a snapshot of 18 public-domain English texts, named in
the NLTK Gutenberg style (`author-title.txt`). They are the collection
the 2012 scripts were pointed at. This page is a catalog of *this*
folder, not a general Gutenberg bibliography.

All of these works are in the public domain in the United States. The
copies here still carry the short NLTK/Gutenberg attribution line at the
top of most files (for example `[Alice's Adventures in Wonderland by
Lewis Carroll 1865]`). Those header tokens are scored like any other
word.

## The 18 documents

Counts below are `wc` line / word / byte counts on the raw files, plus
the number of TF rows (approximate vocabulary after the Perl tokenizer).

| File | Author / work | Lines | `wc` words | Bytes | TF rows |
| --- | --- | ---: | ---: | ---: | ---: |
| `austen-emma.txt` | Jane Austen, *Emma* | 16,823 | 158,167 | 887,071 | 9,312 |
| `austen-persuasion.txt` | Jane Austen, *Persuasion* | 8,471 | 83,308 | 466,292 | 5,990 |
| `austen-sense.txt` | Jane Austen, *Sense and Sensibility* | 14,796 | 118,675 | 673,022 | 7,335 |
| `bible-kjv.txt` | King James Bible | 99,805 | 821,133 | 4,332,554 | 16,567 |
| `blake-poems.txt` | William Blake, *Songs of Innocence and of Experience* (NLTK extract) | 1,441 | 6,845 | 38,153 | 1,542 |
| `bryant-stories.txt` | Sara Cone Bryant, *Stories to Tell to Children* | 5,538 | 45,988 | 249,439 | 4,011 |
| `burgess-busterbrown.txt` | Thornton Burgess, *The Adventures of Buster Bear* | 1,671 | 15,870 | 84,663 | 1,568 |
| `carroll-alice.txt` | Lewis Carroll, *Alice's Adventures in Wonderland* | 3,331 | 26,443 | 144,395 | 2,753 |
| `chesterton-ball.txt` | G. K. Chesterton, *The Ball and the Cross* | 9,548 | 81,598 | 457,450 | 8,646 |
| `chesterton-brown.txt` | G. K. Chesterton, *The Innocence of Father Brown* | 7,654 | 71,626 | 406,629 | 8,235 |
| `chesterton-thursday.txt` | G. K. Chesterton, *The Man Who Was Thursday* | 6,793 | 57,955 | 320,525 | 6,524 |
| `edgeworth-parents.txt` | Maria Edgeworth, *The Parent's Assistant* | 18,297 | 166,070 | 935,158 | 9,561 |
| `melville-moby_dick.txt` | Herman Melville, *Moby-Dick* | 22,924 | 212,030 | 1,242,990 | 19,961 |
| `milton-paradise.txt` | John Milton, *Paradise Lost* | 10,635 | 79,659 | 468,220 | 9,321 |
| `shakespeare-caesar.txt` | Shakespeare, *Julius Caesar* (Folio-flavored text) | 3,523 | 20,459 | 112,310 | 3,091 |
| `shakespeare-hamlet.txt` | Shakespeare, *Hamlet* (Folio-flavored text) | 4,922 | 29,605 | 162,881 | 4,799 |
| `shakespeare-macbeth.txt` | Shakespeare, *Macbeth* (Folio-flavored text) | 3,286 | 17,741 | 100,351 | 3,560 |
| `whitman-leaves.txt` | Walt Whitman, *Leaves of Grass* | 17,435 | 122,070 | 711,215 | 14,568 |

Collection totals from `wc`: 256,893 lines, about 2.14 million words,
11.8 MB. Shared vocabulary in `output/idf.txt`: **57,368** terms.

The Bible is roughly four times as long as *Moby-Dick* and more than a
hundred times as long as Blake. Because TF divides by document length,
that does not by itself give the Bible larger TF-IDF products. It does
give the Bible many more *distinct* rare tokens (verse numbers, names,
archaic forms), which is why its TF table is wide.

## Why this mix is a good TF-IDF demo

The collection is deliberately heterogeneous:

- **Three Austen novels** share a register (and the token `mrs`). IDF
  therefore down-weights society-novel vocabulary that appears in all
  three, and leaves each book's own character names at the top.
- **Three Chesterton books** do the same for early-20th-century
  thriller diction; the surviving top terms are character names
  (`syme`, `flambeau`, `turnbull`).
- **Three Shakespeare plays** are short, verse-heavy, and spelled in a
  Folio-ish way (`haue`, `vs`, `selfe`). Their top weights are often
  speaker tags, not plot words. See [reading-results.md](reading-results.md).
- **One children's book, one nonsense novel, one epic, one scripture,
  one poetry collection** keep IDF from collapsing to "words that are
  rare in realist prose."

A corpus of 18 *similar* news articles would produce blander rankings.
This folder is small enough to rerun on a laptop and diverse enough that
the top-20 lists are immediately recognizable.

## What is *not* in the folder

- No copyrighted modern text.
- No non-English work.
- No duplicate editions of the same title.
- No separate "stopword" or "gold labels" file. Evaluation is
  qualitative: do the top terms look like the book you think you
  opened?

`.DS_Store` files in `gutenberg/` and `output/` are Finder leftovers.
The Perl `^\.` skip means they are not tokenized, but they *do* sit in
the `readdir` array used for \(N\).

## Provenance

These copies match the long-standing NLTK `gutenberg` corpus subset
(filenames and the one-line title headers), not a fresh download from
gutenberg.org. Line breaks and the exact Blake/Bryant extracts follow
that package. If you replace a file with a Project Gutenberg UTF-8
eBook, expect the license boilerplate ("gutenberg", "ebook", "www") to
jump up the TF-IDF list — that already happens in
`chesterton-ball.txt` in this snapshot.

## Suggested reading order

1. `carroll-alice.txt` — short, modern-ish spelling, clean top terms.
2. `burgess-busterbrown.txt` — even shorter; `buster` dominates.
3. `melville-moby_dick.txt` — long book, still a clean "aboutness" list.
4. `shakespeare-hamlet.txt` — same math, messier tokens.
5. `bible-kjv.txt` — archaic function words (`unto`, `saith`) outrank
   theology because they are frequent *and* collection-rare.

Worked top lists for each file live in
[../examples/walkthroughs/gutenberg_top_terms.md](../examples/walkthroughs/gutenberg_top_terms.md).
