# Reading the Gutenberg rankings

These notes walk the committed `output/tfidf/` snapshot the way you would if you were checking that the pipeline did something sensible. Numbers come from `examples/top-terms.pl` and `examples/lookup-term.pl` against the files in this repository; they are not a literary argument.

## *Alice's Adventures in Wonderland*

```bash
perl examples/top-terms.pl --n 10 output/tfidf/carroll-alice.txt
```

| Rank | Token | Approx. TF-IDF |
| ---: | --- | ---: |
| 1 | alice | 0.02596 |
| 2 | gryphon | 0.00455 |
| 3–4 | duchess, dormouse | 0.00424 |
| 5 | hatter | 0.00371 |
| 6 | turtle | 0.00317 |
| 7 | caterpillar | 0.00182 |
| 8 | rabbit | 0.00178 |

`alice` is in a class of its own. The next tier is the supporting cast. `alices` (from `Alice's`) also appears further down because apostrophes were stripped. `lookup-term.pl alice` reports IDF `1.79176`, which is `ln(18/3)`: the token also occurs in `chesterton-thursday.txt` and `edgeworth-parents.txt`. The score is still large because the TF inside Carroll is huge.

## *Moby-Dick*

```bash
perl examples/top-terms.pl --n 10 output/tfidf/melville-moby_dick.txt
```

| Rank | Token | Approx. TF-IDF |
| ---: | --- | ---: |
| 1 | whale | 0.00494 |
| 2 | ahab | 0.00432 |
| 3 | sperm | 0.00326 |
| 4 | stubb | 0.00309 |
| 5 | queequeg | 0.00288 |
| 6 | whales | 0.00276 |
| 7 | starbuck | 0.00230 |
| 8 | pequod | 0.00165 |

Setting vocabulary (`whale`, `sperm`, `nantucket`, `whaling`) sits beside character names. Magnitudes are smaller than `alice` because the book is much longer, so each TF is smaller, and because `whale` has a higher DF (IDF `1.09861` = `ln(18/6)`).

## *Emma*

```bash
perl examples/top-terms.pl --n 10 output/tfidf/austen-emma.txt
```

| Rank | Token | Approx. TF-IDF |
| ---: | --- | ---: |
| 1 | emma | 0.01043 |
| 2 | harriet | 0.00713 |
| 3 | weston | 0.00698 |
| 4 | knightley | 0.00614 |
| 5 | elton | 0.00579 |
| 6 | mr | 0.00418 |
| 7 | fairfax | 0.00367 |

`mr` and `mrs` are high because Austen's dialogue repeats the titles constantly. They are *not* unique to *Emma* — the other Austen novels use them too — so they rank below the *Emma*-only surnames. `lookup-term.pl emma mr` makes that DF gap visible.

## *Hamlet* (formatting wins)

```bash
perl examples/top-terms.pl --n 8 output/tfidf/shakespeare-hamlet.txt
```

The top tokens are `ham`, `haue`, `hor`, `qu`, `laer` — speaker prefixes and Early Modern spelling — not a modern-English character list. `hamlet` appears, but below `ham`. If you want a ranking that looks like the novel tables, strip speaker tags first and keep the cleaned file as the document. See [../docs/interpreting-results.md](../docs/interpreting-results.md).

## King James Bible

```bash
perl examples/top-terms.pl --n 8 output/tfidf/bible-kjv.txt
```

`unto`, `israel`, `saith`, `david`, `judah` lead. The file is so long that only words that are both frequent and somewhat collection-specific survive. Ordinary English is zeroed by IDF; ordinary narrative names from the novels never accumulate enough TF here to compete.

## Blake

Short file, unique mythic names: `thel`, `lyca`, plus `weep` / `weeping`. Header tokens such as `blake` and `1789` can appear in the long tail. That is expected when boilerplate is left in.

## Cross-document lookup

```bash
perl examples/lookup-term.pl the alice whale emma ham hamlet
```

What you should see on the snapshot:

- `the` — IDF `0`, TF-IDF `0` in every file that lists it.
- `alice` — high in Carroll, small or absent elsewhere.
- `whale` — high in Melville, lower where the word is incidental.
- `emma` — high in `austen-emma.txt`, IDF `2.19722` = `ln(18/2)`.
- `ham` vs `hamlet` — the tag beats the name.

If those relationships flip after a rebuild, `N` or the file list changed. Compare `output/idf.txt` to the values above before debugging the product script.
