# Gutenberg toy corpus

These files are public-domain texts bundled with the 2012 toy so the
TF-IDF scripts have something larger than three made-up sentences to
run on. They are **not** a balanced corpus, not a benchmark suite
from any shared-task, and not a dump of a private collection.

Filenames follow the NLTK Gutenberg convention (`author-title.txt`).
I did not re-download them for this documentation pass; the bytes in
`gutenberg/` are the ones the checked-in `output/` tables were built
from.

## Files

Sizes below are the current checkout. Token counts are from the
personal benchmark's Perl-compatible tokenizer (real tokens only,
not the empty split fields).

| File | Rough size | What it is |
| --- | --- | --- |
| `austen-emma.txt` | 887 KB | Jane Austen, *Emma* |
| `austen-persuasion.txt` | 466 KB | Jane Austen, *Persuasion* |
| `austen-sense.txt` | 673 KB | Jane Austen, *Sense and Sensibility* |
| `bible-kjv.txt` | 4.3 MB | King James Bible (dominates collection length) |
| `blake-poems.txt` | 38 KB | William Blake, *Songs of Innocence and of Experience* |
| `bryant-stories.txt` | 249 KB | Sara Cone Bryant, children's stories |
| `burgess-busterbrown.txt` | 85 KB | Thornton Burgess, *The Adventures of Buster Bear* |
| `carroll-alice.txt` | 144 KB | Lewis Carroll, *Alice's Adventures in Wonderland* |
| `chesterton-ball.txt` | 457 KB | G. K. Chesterton, *The Ball and the Cross* |
| `chesterton-brown.txt` | 407 KB | G. K. Chesterton, Father Brown stories |
| `chesterton-thursday.txt` | 321 KB | G. K. Chesterton, *The Man Who Was Thursday* |
| `edgeworth-parents.txt` | 935 KB | Maria Edgeworth, *The Parent's Assistant* |
| `melville-moby_dick.txt` | 1.2 MB | Herman Melville, *Moby-Dick* |
| `milton-paradise.txt` | 468 KB | John Milton, *Paradise Lost* |
| `shakespeare-caesar.txt` | 112 KB | Shakespeare, *Julius Caesar* |
| `shakespeare-hamlet.txt` | 163 KB | Shakespeare, *Hamlet* |
| `shakespeare-macbeth.txt` | 100 KB | Shakespeare, *Macbeth* |
| `whitman-leaves.txt` | 711 KB | Walt Whitman, *Leaves of Grass* |

That is **18 documents**. Hidden files (`.*`, including `.DS_Store`)
are ignored by both the Perl (`if ($f !~ /^\./)`) and the benchmark.

## Why this set is a decent TF-IDF demo

The collection is small enough to read with a laptop and diverse
enough that IDF does real work:

- Three Austen novels share vocabulary with each other, so
  period-romance function words do not dominate a single Austen file
  the way they would in a one-Austen-plus-seventeen-manuals mix.
- Three Chestertons and three Shakespeares do the same for those
  authors.
- The Bible is an outlier in length. Length-normalized TF is what
  keeps it from flooding every global ranking with raw counts.
- Blake is an outlier in the other direction: a short file, so a
  word that appears a handful of times can still have a large TF.

If you add or remove a book, **every IDF value changes**, because
`N` and many `df` counts change. The checked-in `output/` tables
are only valid for this exact 18-file mix.

## What classic TF-IDF actually surfaces here

From one run of `scripts/tfidf_benchmark.py --top 8` (classic,
`N = 18`):

- Austen splits cleanly by proper name: `emma` / `harriet`,
  `elliot` / `wentworth`, `elinor` / `marianne`.
- Carroll, Melville, and Chesterton's *Thursday* do the same with
  `alice`, `whale` / `ahab`, `syme`.
- The Bible's top of the list is function-ish Early Modern English
  (`unto`, `saith`, `thee`) plus names (`israel`, `david`, `judah`).
  Those words are common in that file and scarce in Austen.
- The three Shakespeare files are dominated by **speech prefixes**
  (`ham`, `macb`, `bru`). The tokenizer does not know they are
  stage directions, and IDF treats them as rare content words.
- 221 terms appear in all 18 books and score exactly zero. The
  interesting ranking is everything else.

Exact per-file token and type counts are printed by the benchmark
next to each title. They belong there, not copied here, so a
tokenizer change cannot leave this page stale.

## What the tokenizer does to these texts

Gutenberg editions include titles, chapter labels, and sometimes
bracketed notes. Those are kept as ordinary tokens. After the Perl
cleanup:

- `Alice's` and `Alice` both become `alice` once the apostrophe and
  trailing `s` take different paths (`alice` vs `alices`).
- Hyphenated compounds become concatenations (`mock-turtle` →
  `mockturtle`) because the hyphen is stripped rather than treated
  as a split point. The following space-separated words stay
  separate.
- All-digit strings (`1865`, chapter numbers) survive, which is why
  `output/idf.txt` starts with a long run of numerals.

No file is language-filtered. The whole set is English, so a
single tokenizer is enough.

## Regenerating statistics

```bash
python3 scripts/tfidf_benchmark.py --top 5
```

prints per-file token counts and the current top-weighted terms.
That is the preferred way to refresh the qualitative picture after
you change the tokenizer. Do not edit this page's size column by
hand unless the `gutenberg/` bytes themselves changed.
