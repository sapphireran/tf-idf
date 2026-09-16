# Reading the committed Gutenberg TF-IDF tables

`output/tfidf/` is the 2012 snapshot: one TSV per file in `gutenberg/`,
term in column 1, `tf * idf` in column 2. Nothing in that folder is
secretly a probability. A larger number only means "this term is a bigger
share of this file *and* is uncommon in the other 17 files."

Print the current snapshot without recomputing:

```bash
python3 -m tfidf top-tsv output/tfidf --n 12
```

## What the top terms actually are

### Character names win novels

Austen, Chesterton, Carroll, and Burgess are almost pure cast lists:

| file | top terms |
| --- | --- |
| `austen-emma.txt` | emma, harriet, weston, knightley, elton |
| `austen-persuasion.txt` | elliot, wentworth, anne, musgrove |
| `austen-sense.txt` | elinor, marianne, dashwood, jennings |
| `carroll-alice.txt` | alice, gryphon, duchess, dormouse, hatter |
| `chesterton-thursday.txt` | syme, gregory, professor, marquis |
| `burgess-busterbrown.txt` | buster, browns, joe, blacky, billy |

That is TF-IDF behaving exactly as advertised. A proper name that is
repeated inside one book and almost absent elsewhere is the ideal
high-TF, low-DF term.

### *Moby-Dick* is the cleanest topical example

`whale`, `ahab`, `sperm`, `stubb`, `queequeg`, `pequod`, `nantucket`,
`whaling`, `moby` — this is the list people expect when they hear
"keywords." `sperm` here is the whale, not a random token collision; the
same cleanup that joins `sperm-whale` into `spermwhale` also leaves the
bare adjective `sperm` in "sperm whale."

### The Bible and Milton are dominated by archaic function words

`unto`, `thee`, `thou`, `hath`, `thy` rank above most content nouns.
Those words are common *inside* those files and rarer in Austen or
Burgess, so they get a healthy IDF. They are not topics. They are
register.

If you wanted "aboutness" for `bible-kjv.txt` you would add a stopword
list that includes Early Modern function words, or compare the Bible
only against other Early Modern texts so `unto` loses its IDF.

### Shakespeare files leak speaker tags

The three play texts keep abbreviated speech prefixes:

| file | tags that outrank the plot |
| --- | --- |
| `shakespeare-caesar.txt` | bru, cassi, caes, brut, caska |
| `shakespeare-hamlet.txt` | ham, hor, qu, laer, ophe, pol |
| `shakespeare-macbeth.txt` | macb, macd, mal, banq |

`haue`, `vs`, `vpon`, `heere` are spelling variants (u/v, extra e) that
are rare in the nineteenth-century novels, so they also float up. This is
a reminder that TF-IDF ranks **strings**, not lemmas or modernized
editions.

### Whitman is diffuse

`o`, `thee`, `poems`, `pioneers`, `states`, `manhattan` — *Leaves of
Grass* repeats a small set of address-words across many short poems. No
single character name anchors the file, so the top of the list is quieter
and more generic. Low peak TF-IDF is itself a signal: the document is
less "about one thing" on this particular vocabulary.

## Collection effects

IDF is computed on **these 18 files**, not on English.

- `mr` / `mrs` are characteristic of Austen *in this mix* because the
  plays, the Bible, and *Moby-Dick* do not lean on those honorifics.
- `ebook` and `gutenberg` appear in the Chesterton *Ball and the Cross*
  table. That file still has Project Gutenberg boilerplate, which is rare
  in the other copies here, so boilerplate gets a real weight. Cleaning
  headers would change the ranking.
- Adding a nineteenth novel about whaling would lower `whale`'s IDF and
  reshuffle *Moby-Dick*. The number is not a property of Melville.

## What not to do with these numbers

- Do not average TF-IDF across files and call it a "corpus importance"
  score. IDF already used the whole corpus.
- Do not treat a zero as "the word is absent." It may be present in
  every document.
- Do not compare a term's score in `blake-poems.txt` with the same term
  in `bible-kjv.txt` as if they shared a length prior beyond the TF
  denominator. The committed vectors are not L2-normalized.

## Recomputing

The snapshot used `N = 18` (see `docs/perl-pipeline.md`). The Python CLI
will use 18 again if you point it at `gutenberg/` and leave `.DS_Store`
hidden:

```bash
python3 -m tfidf compute gutenberg -o /tmp/gutenberg-tfidf --idf raw
python3 -m tfidf top /tmp/gutenberg-tfidf/../gutenberg --n 8
```

The second command reads the source texts, not the old TSV. Expect
small numeric drift versus `output/tfidf/` from the empty-field
denominator and from floating-point formatting. Rankings of proper
names should stay stable.
