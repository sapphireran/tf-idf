# Gutenberg toy corpus

`gutenberg/` holds the 18 public-domain files the original Perl run
scored. They are a convenience snapshot, not a balanced corpus and not
a Project Gutenberg mirror.

`N = 18` for every IDF value in `output/idf.txt`.

## Inventory

| File | Author | Work (short) | Why it is in a TF-IDF toy |
| --- | --- | --- | --- |
| `austen-emma.txt` | Jane Austen | *Emma* | Proper names dominate rankings |
| `austen-persuasion.txt` | Jane Austen | *Persuasion* | Same author, different name set |
| `austen-sense.txt` | Jane Austen | *Sense and Sensibility* | Third Austen name set; tests "author vs. book" |
| `bible-kjv.txt` | (KJV) | King James Bible | Archaic function words (`unto`, `saith`) behave like content |
| `blake-poems.txt` | William Blake | Poems | Short file; TF shares are larger |
| `bryant-stories.txt` | Sara Cone Bryant | Stories | Folktale proper names (`epaminondas`, `halfchick`) |
| `burgess-busterbrown.txt` | Thornton Burgess | *Buster Brown* | One character name swamps the ranking |
| `carroll-alice.txt` | Lewis Carroll | *Alice's Adventures in Wonderland* | Clean protagonist + creature names |
| `chesterton-ball.txt` | G. K. Chesterton | *The Ball and the Cross* | Boilerplate leak (`ebook`, `gutenberg`) |
| `chesterton-brown.txt` | G. K. Chesterton | Father Brown stories | Detective-name ranking |
| `chesterton-thursday.txt` | G. K. Chesterton | *The Man Who Was Thursday* | `syme` as a near-unique protagonist token |
| `edgeworth-parents.txt` | Maria Edgeworth | *The Parent's Assistant* | Many story-local names |
| `melville-moby_dick.txt` | Herman Melville | *Moby-Dick* | Classic content words: `whale`, `ahab`, `pequod` |
| `milton-paradise.txt` | John Milton | *Paradise Lost* | `thou`/`thee`/`eve`/`satan` vs. Bible overlap |
| `shakespeare-caesar.txt` | Shakespeare | *Julius Caesar* (Folio-ish) | Speech prefixes (`bru`, `cassi`) |
| `shakespeare-hamlet.txt` | Shakespeare | *Hamlet* | Speech prefixes (`ham`, `hor`, `ophe`) |
| `shakespeare-macbeth.txt` | Shakespeare | *Macbeth* | Speech prefixes (`macb`, `macd`) |
| `whitman-leaves.txt` | Walt Whitman | *Leaves of Grass* | Vocative `o`, place names, `passd` |

## Three useful contrasts

### Same author, different books (Austen)

Emma, Anne Elliot, and Elinor Dashwood do not share a cast. TF-IDF
separates the three Austen files by **character inventory**, not by
"Regency diction." Shared period words (`mrs`, `mr`) still appear,
but they rank below the book-specific names because those names have
lower `df`.

That is the cleanest demonstration in the snapshot that IDF is a
document-rarity weight, not an "old-fashioned English" detector.

### Same genre, different tokenization (Shakespeare)

The three plays are the place where the tokenizer is the story.
Folio speech prefixes are short, repeated, and almost unique to one
file (`ham` vs. `macb` vs. `bru`). They beat the play titles.

If you wanted "literary keywords" you would drop stage prefixes
before scoring. This project does not, on purpose: it shows what the
pipeline actually ranks.

### Boilerplate vs. narrative (Chesterton)

`chesterton-ball.txt` ranks `ebook` and `gutenberg` among its top
terms. Those tokens are not themes of *The Ball and the Cross*. They
are header/license wording that is **unique enough** in this 18-file
set to get a large IDF and **repeated enough** in that one file to
get a visible TF.

The other Chesterton files do not show the same leak at the top,
which is a hint that the boilerplate is not identical across the
three dumps.

## Overlap that IDF can see

Some famous words are less exclusive than they feel:

| Term | Snapshot `idf` | Implied `df` (`18 / e^{idf}`) | Reading |
| --- | ---: | ---: | --- |
| `alice` | 1.79175946922805 | 3 | Carroll plus two other files |
| `whale` | 1.09861228866811 | 6 | Melville plus metaphor / scripture / etc. |
| `hamlet` | 1.09861228866811 | 6 | The name travels |
| `ahab` | 2.19722457733622 | 2 | Nearly exclusive |
| `emma` | 2.19722457733622 | 2 | Nearly exclusive |

A term can be "the" word of a book in memory and still have `df > 1`
in a mixed literary dump. IDF records that overlap; it does not
argue with it.

## What is not in the corpus

- No modern copyrighted novels
- No company documents
- No web crawl
- No parallel translations
- No stopword file
- No gold-standard keywords

The collection is small enough that one extra file changes every IDF.
That is acceptable for a blog-post toy and unacceptable as a search
index.

## Provenance

Texts come from Project Gutenberg. Some files still carry Gutenberg
headers, chapter banners, and license language. Those strings are
tokens. See [limitations.md](limitations.md).
