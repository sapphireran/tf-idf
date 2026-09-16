# Precomputed top terms

Alphabetical dump of the highest tf*idf terms in each Gutenberg file
under `output/tfidf/`, produced by:

```bash
python3 scripts/rank_precomputed_tfidf.py --top 8
```

Scores are copied from the committed 2012 tables (N = 18, natural-log
IDF). Use this as a reading guide, not as a claim that the tokenizer is
linguistically perfect. Shakespeare speaker tags and King James
pronouns show up because the pipeline has no stopword list and no
play-script parser.

## Jane Austen

### emma

| term | tf*idf |
| --- | ---: |
| emma | 0.010432 |
| harriet | 0.007127 |
| weston | 0.006980 |
| knightley | 0.006140 |
| elton | 0.005793 |
| mr | 0.004177 |
| fairfax | 0.003673 |
| woodhouse | 0.003653 |

### persuasion

| term | tf*idf |
| --- | ---: |
| elliot | 0.008813 |
| wentworth | 0.006627 |
| anne | 0.005868 |
| musgrove | 0.003851 |
| russell | 0.003112 |
| mrs | 0.002833 |
| charles | 0.002762 |
| uppercross | 0.002672 |

### sense

| term | tf*idf |
| --- | ---: |
| elinor | 0.015032 |
| marianne | 0.009061 |
| dashwood | 0.005449 |
| jennings | 0.004938 |
| mrs | 0.003590 |
| willoughby | 0.003254 |
| lucy | 0.002903 |
| brandon | 0.002822 |

Character names dominate, which is what you want from a novel-length
bag of words. Place names (`hartfield`, `kellynch`, `barton`) sit just
under the people.

## Lewis Carroll, Thornton Burgess, Herman Melville

### carroll-alice

| term | tf*idf |
| --- | ---: |
| alice | 0.025957 |
| gryphon | 0.004547 |
| dormouse | 0.004242 |
| duchess | 0.004242 |
| hatter | 0.003708 |
| turtle | 0.003169 |
| caterpillar | 0.001820 |
| rabbit | 0.001778 |

### burgess-busterbrown

| term | tf*idf |
| --- | ---: |
| buster | 0.040354 |
| browns | 0.010930 |
| joe | 0.010216 |
| blacky | 0.009270 |
| billy | 0.007089 |
| otter | 0.005634 |
| sammy | 0.005389 |
| chatterer | 0.005271 |

`buster` is the strongest single-term fingerprint in the whole corpus:
the name is very frequent in a short book and almost absent elsewhere.

### melville-moby_dick

| term | tf*idf |
| --- | ---: |
| whale | 0.004943 |
| ahab | 0.004322 |
| sperm | 0.003258 |
| stubb | 0.003095 |
| queequeg | 0.002877 |
| whales | 0.002760 |
| starbuck | 0.002304 |
| pequod | 0.001650 |

No stemming, so `whale` and `whales` are separate terms. Both still
rank, which is a reminder that "the math worked" and "the tokenizer is
done" are different statements.

## Shakespeare (First Folio spelling)

Speaker abbreviations outrank character names because they repeat on
almost every line of dialogue.

### macbeth

| term | tf*idf |
| --- | ---: |
| macb | 0.021556 |
| haue | 0.011900 |
| macbeth | 0.009755 |
| macd | 0.009126 |
| rosse | 0.007710 |
| vpon | 0.005657 |
| vs | 0.005365 |
| banquo | 0.005350 |

### hamlet

| term | tf*idf |
| --- | ---: |
| ham | 0.014075 |
| haue | 0.010224 |
| hor | 0.006806 |
| qu | 0.005843 |
| laer | 0.005655 |
| ophe | 0.005278 |
| pol | 0.004618 |
| rosin | 0.004052 |

### caesar

| term | tf*idf |
| --- | ---: |
| bru | 0.020821 |
| brutus | 0.016656 |
| cassi | 0.014561 |
| haue | 0.012401 |
| cassius | 0.011567 |
| antony | 0.007759 |
| caesar | 0.007254 |
| caes | 0.005307 |

`haue` / `vs` / `vpon` are period spelling for *have*, *us*, *upon*.
They look "distinctive" only because the rest of the corpus is mostly
later English.

## Other books

### bible-kjv

| term | tf*idf |
| --- | ---: |
| unto | 0.012037 |
| israel | 0.004001 |
| saith | 0.003377 |
| thee | 0.002295 |
| david | 0.002206 |
| judah | 0.002173 |
| thou | 0.002169 |
| hath | 0.001911 |

Archaic function words beat many proper names because they are common
*inside* this document and rarer in Austen or Burgess.

### blake-poems

| term | tf*idf |
| --- | ---: |
| thel | 0.005581 |
| weep | 0.003957 |
| lyca | 0.002976 |
| thee | 0.002662 |
| vales | 0.001742 |
| oer | 0.001697 |
| har | 0.001488 |
| thou | 0.001466 |

### chesterton-thursday

| term | tf*idf |
| --- | ---: |
| syme | 0.024354 |
| gregory | 0.003908 |
| professor | 0.003229 |
| marquis | 0.002944 |
| secretary | 0.002011 |
| gogol | 0.001747 |
| anarchists | 0.001647 |
| symes | 0.001597 |

### chesterton-ball

| term | tf*idf |
| --- | ---: |
| turnbull | 0.017951 |
| macian | 0.014623 |
| evan | 0.004603 |
| turnbulls | 0.001275 |
| ebook | 0.000956 |
| police | 0.000884 |
| madeleine | 0.000850 |
| have | 0.000840 |

`ebook` is a pipeline smell: leftover Project Gutenberg boilerplate
that is not distributed evenly across the 18 files.

### chesterton-brown, bryant-stories, edgeworth-parents, milton, whitman

| file | top terms (8) |
| --- | --- |
| chesterton-brown | flambeau, boulnois, muscari, fanshaw, brown, todhunter, seymour, hirsch |
| bryant-stories | margery, jackal, brahmin, epaminondas, nightingale, halfchick, tailor, david |
| edgeworth-parents | cecilia, susan, piedro, jem, leonora, archer, hal, mr |
| milton-paradise | thee, thou, heaven, thy, eve, th, adam, hath |
| whitman-leaves | o, thee, poems, pioneers, states, passd, chant, cities |

Milton and Whitman are a useful failure case: without a stopword list,
archaic pronouns and the letter `o` compete with actual content.
