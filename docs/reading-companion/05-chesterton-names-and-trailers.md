# Chesterton: names versus license trailers

G. K. Chesterton contributes three files and they barely cluster:

| Pair | Cosine |
| --- | ---: |
| Ball ↔ Father Brown | 0.0523 |
| Thursday ↔ Father Brown | 0.0510 |
| Ball ↔ Thursday | 0.0222 |
| **intra-Chesterton mean** | **0.0418** |

That is weaker than Austen (0.074) and nowhere near Shakespeare
(0.262). The cause is the same name-spike rule, plus one file that
swallowed a Project Gutenberg license.

## Three books, three private dictionaries

| File | Top terms | What they are |
| --- | --- | --- |
| *The Ball and the Cross* | turnbull 0.01795, macian 0.01462, evan 0.00460 | the two duelists and a given name |
| Father Brown | flambeau 0.00489, then a trail of one-story surnames | a collection, so the spike is muted |
| *The Man Who Was Thursday* | syme 0.02435, gregory, professor, marquis, gogol, anarchists | one novel, one hero, one conspiracy |

A query of `syme anarchist professor` returns Thursday at 0.6452,
with Ball a distant 0.0071 (shared Chesterton furniture, not the
plot). `flambeau priest brown` returns the Father Brown file at
0.4823. The novels do not leak cast members into each other.

Father Brown's top weight is an order of magnitude smaller than
`syme` or `turnbull` because the file is a bundle of mysteries. That
is the same collection-versus-novel contrast as Edgeworth versus
*Sense and Sensibility*.

## The trailer that entered the top ten

*The Ball and the Cross* is the only file on the shelf whose top
fifteen include the publishing wrapper:

| Rank-ish term | Weight | Why it is there |
| --- | ---: | --- |
| ebook | 0.000956 | Gutenberg "Small Print" / eBook trailer |
| gutenberg | 0.000744 | same trailer, repeated |
| ebooks | 0.000602 | same |

The narrative begins cleanly:

```
[The Ball and The Cross by G.K. Chesterton 1909]
I. A DISCUSSION SOMEWHAT IN THE AIR
```

Around line 9228 the file switches to

```
End of Project Gutenberg's The Ball and The Cross...
*** END OF THE PROJECT GUTENBERG EBOOK THE BALL AND THE CROSS ***
```

and then several hundred lines of license, donation, and `eBook`
boilerplate. The tokenizer has no header/trailer detector. `ebook`
is a `df = 1` token on this snapshot (`idf ≈ 2.890`), so a few dozen
repetitions in an 82k-word file are enough to outrank most of the
novel's ordinary verbs.

This is not Chesterton developing a theme of electronic books in
1909. It is a reminder that "the document" for these scripts is the
byte file, including legal text. Other books on the shelf have
shorter or absent trailers, so the words stay rare *and* file-local.

`python3 examples/reading-companion/boilerplate_scan.py` counts raw
`gutenberg` / `ebook` / `ebooks` hits in each `gutenberg/*.txt`
file and lines them up against snapshot weights. Ball is the
outlier.

## How to read Chesterton on this shelf

- Treat each file as its own island. Author-level clustering fails
  when each book is a proper-name spike.
- Drop `ebook`, `gutenberg`, and `ebooks` from *Ball* before you
  decide what the novel is about. What remains is `turnbull`,
  `macian`, `highlander`, `madeleine`, `quayle`.
- Father Brown is the "Chesterton residual": lower spikes, slightly
  closer to other late-Victorian/Edwardian prose (it is Edgeworth's
  third-ish neighbor at 0.0995, and Whitman's at 0.0879). That is
  shared journalistic vocabulary, not a secret Father Brown cameo
  in *Leaves of Grass*.
