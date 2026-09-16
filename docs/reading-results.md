# How to read the scores

`output/tfidf/<doc>.txt` is an alphabetical dump, not a ranking. Sort
the second column descending, or run:

```bash
python3 examples/rank_terms.py --input-dir output/tfidf --top 15
```

The number on each line is \(\mathrm{tf} \times \mathrm{idf}\) for that
token in that document. Larger means "more characteristic of this file
relative to the other 17," not "more important in English."

## Patterns that mean the method is working

**Character names win novels.** *Emma* ranks `emma`, `harriet`,
`weston`, `knightley`, `elton`. *Persuasion* ranks `elliot`,
`wentworth`, `anne`. *Thursday* ranks `syme`. *Alice* ranks `alice`,
then the set pieces (`gryphon`, `duchess`, `dormouse`, `hatter`).
*Moby-Dick* ranks `whale`, `ahab`, `sperm`, `stubb`, `queequeg`. That is
TF-IDF doing the job it was designed for: a name that is the air the
book breathes, and almost nobody else's air.

**Shared genre words get suppressed.** `mrs` still appears in the Austen
top 15 because it is frequent, but it is weaker than the unique
surnames. `whale` beats `the` by construction.

**Short books produce larger raw products.** Buster Bear's top score is
`0.040` (`buster`). *Moby-Dick*'s top score is `0.005` (`whale`). The
bear book is not "eight times more about Buster" than *Moby-Dick* is
about whales. \(|d|\) is smaller, so every TF is larger. Compare ranks
inside a file, or compare the *identity* of top terms across files, not
the raw magnitudes.

## Patterns that look like bugs and usually are not

### Function words with IDF 0

`a`, `the`, and `and` have IDF `0` in `output/idf.txt` because they
appear in all 18 files. Their TF-IDF is identically zero everywhere.
That is the definition working. It is also why this toy never needed a
stopword list for the most common English words — *as long as every
document is a long English text*. Add a Latin poem or an empty file and
`the` suddenly gets a nonzero IDF.

### Archaic words that are not "about" the book

The King James Bible's top term is `unto`, then `israel`, `saith`,
`thee`. `unto` and `saith` are grammatical fossils. They are rare in
Austen and Chesterton, so IDF treats them like content. The same thing
happens to `thee` / `thou` / `thy` in Milton. If you want topical words
only, you need a stopword list that includes Early Modern function
words, or a different weighting (see [quirks-and-variants.md](quirks-and-variants.md)).

### Speaker tags in the plays

Top of *Hamlet*: `ham`, `haue`, `hor`, `qu`, `laer`, `ophe`. Those are
Folio speech prefixes (`Ham.`, `Hor.`, `Qu.`, `Laer.`, `Ophe.`) after
punctuation stripping, plus the period spelling `haue` for *have*.
`hamlet` itself is lower because the name is written out less often than
the tag. TF-IDF is correctly finding what this *file* is full of. It is
not finding "the theme of Hamlet."

### Gutenberg / ebook tokens

`chesterton-ball.txt` places `ebook` and `gutenberg` in the top 15.
That file's header/footer is heavier than the others, so the license
language is collection-rare *and* repeated. Strip boilerplate before
tokenizing if you want only story words. The mini-corpus examples have
no headers so this effect is absent there.

### Morphology and glued tokens

`alices`, `whales`, `turnbulls`, `symes` are separate terms from their
stems. `dont`, `oer`, `passd` are apostrophe/diacritic casualties.
`thethe` and `whalethe` in `output/idf.txt` are almost certainly two
words that lost their separating punctuation or line-break hyphen and
got concatenated. The tokenizer does not split on case or recover
hyphens.

## Comparing two books

Do not subtract TF-IDF vectors componentwise and expect a clean
"difference summary" without more work: the vocabularies are large, and
length normalization is only inside each TF. Cosine similarity on the
sparse TF-IDF vectors *is* a reasonable next step; it cancels magnitude
and asks "do these books emphasize the same rare words?"

`examples/cosine_similarity.py` does that for the mini-corpus and can
point at `output/tfidf` for a Gutenberg pairwise table. On the
committed run the top pairs are **not** "same author":

- Shakespeare plays cluster first (`hamlet`–`macbeth` 0.31). They
  share Folio leftovers (`haue`, `vs`, `thee`) and speech-prefix
  shapes.
- Milton, Whitman, Blake, and the KJV form a second clump of Early
  Modern / vocative diction (`thee`, `thou`, `o`).
- Each Austen novel is closer to Edgeworth (`mrs`, `mr`) than the
  three Austen files are to each other. Character names dominate
  TF-IDF and do not overlap, so *Emma* and *Sense and Sensibility*
  look like different books — which they are, token-wise.
- Burgess vs any Shakespeare play is ~0.0002–0.0005, the floor of
  the table.

Those similarities are still bag-of-tokens similarities. The script
does not know two files are "both Austen"; it knows they share rare
tokens. Unique names are rare *and* unshared, so they push
same-author novels apart. That is a feature of this weighting, not
a bug in the cosine code.

## A checklist before you trust a top term

1. Is it a **name or topic word** you recognize from the book? Good.
2. Is it a **speech prefix, verse number, or license word**? The file
   contains that string a lot; consider cleaning the input.
3. Is it an **archaic function word**? IDF thinks it is rare in *this
   collection*, not rare in English.
4. Is the score **large only because the file is short**? Look at rank,
   not the absolute value.
5. Does the same word **also top a different book**? Then it is only
   mildly rare (`caesar` appears in 8 of 18 files; it still ranks in
   *Julius Caesar*, but its IDF is just \(\ln(18/8) \approx 0.811\)).

For annotated top-15 lists, see
[../examples/walkthroughs/gutenberg_top_terms.md](../examples/walkthroughs/gutenberg_top_terms.md).
