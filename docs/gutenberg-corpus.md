# Gutenberg collection notes

`gutenberg/` is a flat directory of 18 public-domain texts. They are a
convenience dump for the 2012 blog post, not a curated literary corpus.
File names follow `author-shorttitle.txt`.

## Sizes

Approximate on-disk sizes of the committed texts:

| File | Bytes (approx.) | Role in the collection |
| --- | --- | --- |
| `bible-kjv.txt` | 4.3 MB | Longest file; many hapax spellings and verse numbers |
| `melville-moby_dick.txt` | 1.2 MB | Distinctive whaling vocabulary |
| `edgeworth-parents.txt` | 0.9 MB | Children's moral tales |
| `austen-emma.txt` | 0.9 MB | One of three Austen novels |
| `whitman-leaves.txt` | 0.7 MB | Catalog-style repetition |
| `austen-sense.txt` | 0.7 MB | Austen |
| `milton-paradise.txt` | 0.5 MB | Early Modern epic |
| `austen-persuasion.txt` | 0.5 MB | Austen |
| `chesterton-ball.txt` | 0.5 MB | Chesterton novel |
| `chesterton-brown.txt` | 0.4 MB | Father Brown |
| `chesterton-thursday.txt` | 0.3 MB | Chesterton novel |
| `bryant-stories.txt` | 0.2 MB | Short stories |
| `shakespeare-hamlet.txt` | 0.2 MB | Play, speech prefixes |
| `carroll-alice.txt` | 0.14 MB | Children's novel |
| `shakespeare-caesar.txt` | 0.11 MB | Play |
| `shakespeare-macbeth.txt` | 0.10 MB | Play |
| `burgess-busterbrown.txt` | 0.08 MB | Children's animal story |
| `blake-poems.txt` | 0.04 MB | Shortest file |

Normalized tf already divides by document length, so Blake is not
drowned by the KJV. A term that occurs 10 times in Blake can outrank a
term that occurs 10 times in the Bible.

## Tokenization artifacts you will see in `output/`

The Perl normalizer is deliberately crude.

- **Apostrophes vanish.** `Alice's` becomes `alices` (a real top term
  in the Alice file). `don't` becomes `dont`.
- **Speech prefixes win Shakespeare.** `ham`, `hor`, `ophe`, `laer` are
  abbreviated speaker tags, not vocabulary from the verse. `haue` /
  `giue` / `vpon` are Early Modern spellings (`u`/`v` interchange).
- **Digits stay.** Project Gutenberg header ids and biblical verse
  numbers become tokens (`1865`, `00021053`). A one-document number
  gets `idf = ln(18)` and can look “important” if it repeats.
- **No stemming.** `whale`, `whales`, `whaling`, `whalemen` are four
  terms. They all rank in *Moby-Dick* because each is still rare
  outside that file.
- **Cross-file leakage.** `alice` has `idf = ln(6)`, so it appears in
  three of the 18 files, not one. A mention in another book lowers the
  Alice-file score a little; it does not remove the name from the top.

## Sample rankings from the committed tables

Top terms in `output/tfidf/`, after dropping zeros. Full lists for every
file are in [`examples/gutenberg-top-terms.md`](../examples/gutenberg-top-terms.md).

**carroll-alice.txt:** alice, gryphon, duchess, dormouse, hatter, turtle,
caterpillar, rabbit, alices, herself.

**melville-moby_dick.txt:** whale, ahab, sperm, stubb, queequeg, whales,
starbuck, pequod, nantucket, boats.

**shakespeare-hamlet.txt:** ham, haue, hor, qu, laer, ophe, pol, rosin,
selfe, loue.

**blake-poems.txt:** thel, weep, lyca, thee, vales, oer, har, thou,
weeping, lamb.

**milton-paradise.txt:** thee, thou, heaven, thy, eve, th, adam, hath,
spake, satan.

Names and setting words behave as advertised. Pronouns (`thee`, `thou`,
`thy`) rank in Milton and Blake because several other files are modern
prose and barely use them — idf treats “archaic pronoun” the same way
it treats “Pequod”.

## How to rank without recomputing

```bash
python3 examples/python/top_terms.py \
  --from-output output/tfidf \
  --file carroll-alice.txt \
  --top 15
```

Omit `--file` to print a section for every document. That is how
`examples/gutenberg-top-terms.md` is produced.

## Recompute (does not overwrite `output/`)

```bash
python3 examples/python/tfidf.py \
  --input gutenberg \
  --output examples/_scratch/gutenberg \
  --top 10
```

Hidden names (`.DS_Store`) are skipped. `N` is the number of files
actually read (18), not `$#files`.
