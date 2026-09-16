# Top 10 tf-idf terms per Gutenberg file

Generated from the checked-in `output/tfidf` snapshot with:

```bash
python3 examples/top_terms.py --path output/tfidf --n 10
```

Use this page as an index. Interpretation of five of the files is in [interpreting-results.md](interpreting-results.md). Scores are rounded to five decimals.

## Jane Austen

Three novels, three disjoint name lists. That is the sanity check that each file is its own document.

| *Emma* | *Persuasion* | *Sense and Sensibility* |
| --- | --- | --- |
| emma 0.01043 | elliot 0.00881 | elinor 0.01503 |
| harriet 0.00713 | wentworth 0.00663 | marianne 0.00906 |
| weston 0.00698 | anne 0.00587 | dashwood 0.00545 |
| knightley 0.00614 | musgrove 0.00385 | jennings 0.00494 |
| elton 0.00579 | russell 0.00311 | mrs 0.00359 |
| mr 0.00418 | mrs 0.00283 | willoughby 0.00325 |
| fairfax 0.00367 | charles 0.00276 | lucy 0.00290 |
| woodhouse 0.00365 | uppercross 0.00267 | brandon 0.00282 |
| mrs 0.00352 | kellynch 0.00253 | ferrars 0.00265 |
| jane 0.00308 | captain 0.00252 | barton 0.00216 |

Shared `mrs` / `mr` / `captain` are honorifics, not plot bleed.

## Lewis Carroll — *Alice’s Adventures in Wonderland*

alice 0.02596, gryphon 0.00455, dormouse 0.00424, duchess 0.00424, hatter 0.00371, turtle 0.00317, caterpillar 0.00182, rabbit 0.00178, alices 0.00131, herself 0.00127

## Herman Melville — *Moby-Dick*

whale 0.00494, ahab 0.00432, sperm 0.00326, stubb 0.00309, queequeg 0.00288, whales 0.00276, starbuck 0.00230, pequod 0.00165, nantucket 0.00130, boats 0.00127

## William Shakespeare

Speaker tags dominate. Full names sit lower.

| *Hamlet* | *Macbeth* | *Julius Caesar* |
| --- | --- | --- |
| ham 0.01408 | macb 0.02156 | bru 0.02082 |
| haue 0.01022 | haue 0.01190 | brutus 0.01666 |
| hor 0.00681 | macbeth 0.00976 | cassi 0.01456 |
| qu 0.00584 | macd 0.00913 | haue 0.01240 |
| laer 0.00565 | rosse 0.00771 | cassius 0.01157 |
| ophe 0.00528 | vpon 0.00566 | antony 0.00776 |
| pol 0.00462 | vs 0.00536 | caesar 0.00725 |
| rosin 0.00405 | banquo 0.00535 | caes 0.00531 |
| selfe 0.00391 | lenox 0.00441 | vs 0.00523 |
| loue 0.00380 | mal 0.00393 | brut 0.00504 |

`haue` / `vs` / `vpon` are First Folio spellings shared across the three plays, so their idf is lower than a name that occurs in only one play — and they still rank because they are so frequent inside each play.

## G. K. Chesterton

| *The Man Who Was Thursday* | Father Brown stories | *The Ball and the Cross* |
| --- | --- | --- |
| syme 0.02435 | flambeau 0.00489 | turnbull 0.01795 |
| gregory 0.00391 | boulnois 0.00195 | macian 0.01462 |
| professor 0.00323 | muscari 0.00179 | evan 0.00460 |
| marquis 0.00294 | fanshaw 0.00131 | turnbulls 0.00127 |
| secretary 0.00201 | brown 0.00125 | **ebook 0.00096** |
| gogol 0.00175 | hirsch 0.00107 | police 0.00088 |
| anarchists 0.00165 | seymour 0.00107 | madeleine 0.00085 |
| symes 0.00160 | todhunter 0.00107 | have 0.00084 |
| anarchist 0.00156 | priest 0.00106 | highlander 0.00081 |
| president 0.00148 | cutler 0.00103 | **gutenberg 0.00074** |

`ebook` and `gutenberg` in *The Ball and the Cross* are license-banner tokens. tf-idf has no notion of “boilerplate.” If a header is unique to one file, it ranks.

## Other prose and verse

**King James Bible.** unto 0.01204, israel 0.00400, saith 0.00338, thee 0.00229, david 0.00221, judah 0.00217, thou 0.00217, hath 0.00191, lord 0.00174, jesus 0.00153

`unto` / `saith` / `hath` are translation style. `thee` / `thou` are shared with Milton and Blake, so they are not as dominant as `unto`.

**Milton, *Paradise Lost*.** thee 0.00220, thou 0.00176, heaven 0.00144, thy 0.00130, eve 0.00116, th 0.00114, adam 0.00111, hath 0.00098, spake 0.00085, satan 0.00082

`th` is often the remnant of `th'` / `th.` after punctuation stripping.

**Blake, poems.** thel 0.00558, weep 0.00396, lyca 0.00298, thee 0.00266, vales 0.00174, oer 0.00170, har 0.00149, thou 0.00147, lamb 0.00146, weeping 0.00146

**Whitman, *Leaves of Grass*.** o 0.00183, thee 0.00099, poems 0.00085, pioneers 0.00077, states 0.00077, passd 0.00076, chant 0.00073, cities 0.00064, forever 0.00064, soul 0.00060

`o` is the vocative (“O pioneer”). Magnitudes are small because the file is long and Whitman’s lexicon overlaps the rest of the collection more than Alice’s does.

**Burgess, *Buster Bear*.** buster 0.04035, browns 0.01093, joe 0.01022, blacky 0.00927, billy 0.00709, otter 0.00563, sammy 0.00539, chatterer 0.00527, trout 0.00511, mink 0.00509

Highest top-term score in the snapshot. Short children’s book, repeated character names, almost no leakage into the other 17 files.

**Bryant, stories.** margery 0.00375, jackal 0.00370, brahmin 0.00209, epaminondas 0.00200, nightingale 0.00194, halfchick 0.00162, tailor 0.00153, david 0.00143, alligator 0.00124, big 0.00121

A story-title list. `david` also lives in the KJV, so it is weaker here than a nonce name like `halfchick`.

**Edgeworth, *The Parent’s Assistant*.** cecilia 0.00268, susan 0.00259, piedro 0.00243, jem 0.00193, leonora 0.00179, archer 0.00179, hal 0.00174, mr 0.00162, francisco 0.00156, mrs 0.00147

## Patterns that show up only when you see every file

1. **Proper names win** whenever the input is modern prose with a stable cast (Austen, Burgess, Chesterton’s *Thursday*, Alice, *Moby-Dick*).
2. **Format wins** when the input is a play (Shakespeare) or a file that kept its Gutenberg banner (Chesterton’s *Ball*).
3. **Shared archaic diction** (`thee`, `thou`, `haue`) ranks mid-to-high in verse and scripture because frequency inside the file is enormous, even though df is not 1.
4. **Length shrinks magnitudes**, not ranks. Whitman’s #1 is 0.0018; Burgess’s #1 is 0.040. Both are “the most distinctive token in that file.”

Regenerate this table after any Perl re-run; do not edit the numbers by hand.
