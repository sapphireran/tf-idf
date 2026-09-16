# Gutenberg sample corpus

The collection is the `gutenberg/` directory: **18** plain-text books. Each file is one document. There is no extra metadata file; the filename is the document id used in `output/df.txt`.

These notes exist so you can interpret a high score without opening the whole book. Line counts are `wc -l` on the checked-in files.

## Catalog

| File | Approx. lines | Work | Why it is in the sample |
| --- | ---: | --- | --- |
| `blake-poems.txt` | 1,441 | William Blake, *Songs of Innocence and of Experience* (and related short poems) | Shortest literary file. Archaic second-person (`thee`, `thou`, `thy`) and song-like repetition (`weep`, `lamb`). |
| `burgess-busterbrown.txt` | 1,671 | Thornton W. Burgess, *The Adventures of Buster Bear* | Early-20th-century children’s animal story. Character names (`buster`, `farmer`, woodland animals) are naturally rare elsewhere. |
| `shakespeare-macbeth.txt` | 3,286 | *Macbeth* | Tragedy with a small cast. Speaker prefixes and Scottish place names separate it from the comedies and from *Hamlet*. |
| `carroll-alice.txt` | 3,331 | Lewis Carroll, *Alice’s Adventures in Wonderland* (1865) | Invented creatures (`gryphon`, `dormouse`, `hatter`) plus the title character. Best first file to read in `output/tfidf`. |
| `shakespeare-caesar.txt` | 3,523 | *Julius Caesar* | Roman proper names (`brutus`, `cassius`, `antony`) and a different speaker-tag set from *Hamlet*. |
| `shakespeare-hamlet.txt` | 4,922 | *Hamlet* (First Folio-style spelling in this dump) | Highest density of **orthography artifacts**: `haue`, `selfe`, `loue`, `vs`, `giue`, plus abbreviated speaker tags `ham`, `hor`, `ophe`. |
| `bryant-stories.txt` | 5,538 | Sara Cone Bryant, children’s stories | Narrative prose aimed at children; fewer nonce names than Carroll, more ordinary story verbs. |
| `chesterton-thursday.txt` | 6,793 | G. K. Chesterton, *The Man Who Was Thursday* | Edwardian thriller-allegory. Recurring surnames (`syme`, `gregory`) should outrank shared English vocabulary. |
| `chesterton-brown.txt` | 7,654 | G. K. Chesterton, Father Brown stories | Detective-priest proper names (`brown`, `flambeau`) plus “father” in a clerical sense that other books do not share at the same rate. |
| `austen-persuasion.txt` | 8,471 | Jane Austen, *Persuasion* | Navy/Kellynch social world: `wentworth`, `elliot`, `anne`. Contrast with *Emma* and *Sense and Sensibility*. |
| `chesterton-ball.txt` | 9,548 | G. K. Chesterton, *The Ball and the Cross* | Third Chesterton file. Shared Chesterton diction is partly cancelled by idf; book-specific names should remain. |
| `milton-paradise.txt` | 10,635 | John Milton, *Paradise Lost* | Epic blank verse. Theological proper names (`satan`, `adam`, `eve`, `heaven`) and Latinate diction. |
| `austen-sense.txt` | 14,796 | Jane Austen, *Sense and Sensibility* | Dashwood / Ferrars / Willoughby names vs. the Emma/Highbury set. |
| `austen-emma.txt` | 16,823 | Jane Austen, *Emma* | Clean character-name ranking: `emma`, `harriet`, `weston`, `knightley`, `elton`, `hartfield`, `highbury`. |
| `whitman-leaves.txt` | 17,435 | Walt Whitman, *Leaves of Grass* | Catalog rhetoric and first-person plural America. High scores should be Whitman-specific nouns, not `the`. |
| `edgeworth-parents.txt` | 18,297 | Maria Edgeworth, *The Parent’s Assistant* (stories) | Didactic children’s tales; character and story titles matter more than function words. |
| `melville-moby_dick.txt` | 22,924 | Herman Melville, *Moby-Dick* | Classic tf-idf demo: `whale`, `ahab`, `sperm`, `queequeg`, `pequod`, `nantucket`. |
| `bible-kjv.txt` | 99,805 | King James Bible | Outlier length. Verse numbers and names (`unto`, `lord`, `israel`, `thee`) appear constantly *inside* the file; idf still depends on how many *other* files use those words. |

Total: **256,893** lines in the checked-in snapshot.

## How length interacts with tf-idf

Term frequency in this repo is **normalized by token count**, not raw count. A word used 20 times in Blake can outrank a word used 20 times in the KJV, because Blake is much shorter.

Document frequency ignores length: a word that appears once in the Bible and once in Blake has \(\mathrm{df} = 2\), same as a word that appears a thousand times in both.

That combination is why *Moby-Dick*’s `whale` is a high score (frequent in one long book, rare in the other seventeen) and why `the` is not.

## Filename convention

Most files are `author-shorttitle.txt`. The scripts never parse the author. `output/df.txt` lists the same basename, comma-separated, for every term.

## Encoding and cleanup already applied

The files are already Gutenberg-style plain text with a one-line title header on several of them (Alice begins `[Alice's Adventures in Wonderland by Lewis Carroll 1865]`). The pipeline does **not** strip Gutenberg license banners if present; any boilerplate tokens become ordinary terms. If a header word is unique to one file, it can appear in that file’s top ranks. Alice’s `1865` is an example of a header token that survives tokenization as a digit sequence.

## Three kinds of “distinctive” terms you will see

1. **True content names.** `alice`, `ahab`, `highbury`, `pequod`. These are the intended teaching examples.
2. **Morphological twins.** `whale` / `whales`, `elton` / `eltons`. No stemmer, so both survive.
3. **Format artifacts.** Shakespeare speaker tags (`ham`, `hor`, `laer`), First Folio spelling (`haue`, `selfe`), honorifics that Austen uses constantly (`mr`, `mrs`). They are mathematically correct and narratively misleading.

[docs/interpreting-results.md](interpreting-results.md) walks ranked lists for five of the files with these three buckets labeled. [docs/gutenberg-top-terms.md](gutenberg-top-terms.md) lists the top 10 for every file.

## Suggested reading order

If you only open a few texts while learning the pipeline:

1. `carroll-alice.txt` — invented lexicon, easy to eyeball.
2. `melville-moby_dick.txt` — the textbook “aboutness” example.
3. `austen-emma.txt` — character graph as a ranking.
4. `shakespeare-hamlet.txt` — same method, messier tokens.
5. `blake-poems.txt` — short file, archaic pronouns, repetition.

Then run the five-document toy corpus in `examples/tiny-corpus/` so you can compute the same formulas by hand.
