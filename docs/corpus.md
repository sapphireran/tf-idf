# Gutenberg pocket corpus

Eighteen public-domain texts. Each file keeps a one-line Project Gutenberg-style header in square brackets, then the work itself. Line counts below are `wc -l` on the files in this tree (headers included).

| File | Work | Author | Lines |
| --- | --- | --- | --- |
| `austen-emma.txt` | *Emma* | Jane Austen | 16,823 |
| `austen-persuasion.txt` | *Persuasion* | Jane Austen | 8,471 |
| `austen-sense.txt` | *Sense and Sensibility* | Jane Austen | 14,796 |
| `bible-kjv.txt` | King James Bible | (compilation) | 99,805 |
| `blake-poems.txt` | *Songs of Innocence and of Experience* and *The Book of Thel* | William Blake | 1,441 |
| `bryant-stories.txt` | *Stories to Tell to Children* | Sara Cone Bryant | 5,538 |
| `burgess-busterbrown.txt` | *The Adventures of Buster Bear* | Thornton W. Burgess | 1,671 |
| `carroll-alice.txt` | *Alice’s Adventures in Wonderland* | Lewis Carroll | 3,331 |
| `chesterton-ball.txt` | *The Ball and the Cross* | G. K. Chesterton | 9,548 |
| `chesterton-brown.txt` | *The Wisdom of Father Brown* | G. K. Chesterton | 7,654 |
| `chesterton-thursday.txt` | *The Man Who Was Thursday* | G. K. Chesterton | 6,793 |
| `edgeworth-parents.txt` | *The Parent’s Assistant* | Maria Edgeworth | 18,297 |
| `melville-moby_dick.txt` | *Moby-Dick* | Herman Melville | 22,924 |
| `milton-paradise.txt` | *Paradise Lost* | John Milton | 10,635 |
| `shakespeare-caesar.txt` | *Julius Caesar* | William Shakespeare | 3,523 |
| `shakespeare-hamlet.txt` | *Hamlet* | William Shakespeare | 4,922 |
| `shakespeare-macbeth.txt` | *Macbeth* | William Shakespeare | 3,286 |
| `whitman-leaves.txt` | *Leaves of Grass* | Walt Whitman | 17,435 |

## Why this mix works as a demo

The collection is **heterogeneous on purpose**:

- **Three Austen novels** share a diction (`emma` is still a good identifier because the other two books are not *Emma*).
- **Three Shakespeare plays** share Early Modern English (`thou`, `thee`, verse stage directions) but keep distinct cast lists (`macbeth` vs `hamlet` vs `caesar`).
- **Three Chesterton books** share an authorial voice; plot-specific names still rise.
- **One whale novel**, **one children’s animal story**, **one dream-logic children’s novel**, **scripture**, **blank verse epic**, **lyric poetry**.

idf is a statement about *this* mix. `whale` is only moderately rare (it leaks into other files as metaphor or scripture). `gryphon` is essentially Alice’s.

## Collection-size effects

The KJV is by far the longest file. Because tf is length-normalized, the Bible does not automatically win every ranking. It *does* dominate **document frequency** for biblical names and archaic pronouns: those terms become worse discriminators for Milton and Shakespeare than they would be in a corpus without the KJV.

Blake and Burgess are short. A word that appears three times in Blake can have a large tf simply because the denominator is small. Short documents look “spikier.” That is a feature of normalized tf, not a bug in the file.

## Headers and metadata

The bracketed first line (`[Alice's Adventures in Wonderland by Lewis Carroll 1865]`) is tokenized like any other sentence. Year tokens such as `1865` appear in the tf tables. They rarely win a ranking, but they are not stripped.

Stage directions, book numbers (`Book I`), and chapter titles are kept. `chapter` is a moderately common heading word and is a weak identifier.

## Provenance

These are the texts that shipped with the original 2012 toy commit. They are **not** a complete Gutenberg catalog and they are not necessarily the latest PG plain-text editions. If you replace a file, regenerate `output/` before comparing scores to the numbers quoted in these docs.
