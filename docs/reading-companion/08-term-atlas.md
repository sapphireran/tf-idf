# Term atlas

Top fifteen snapshot terms for every file, with a one-line reading.
Regenerate the raw lists with:

```bash
python3 examples/reading-companion/term_atlas.py --top 15
```

Scores are rounded. Ties are not expected at this precision.

## austen-emma.txt — *Emma*

| Term | Score | Note |
| --- | ---: | --- |
| emma | 0.01043 | title character; `df = 2` |
| harriet | 0.00713 | Harriet Smith |
| weston | 0.00698 | the Weston marriage plot |
| knightley | 0.00614 | Mr. Knightley |
| elton | 0.00579 | the Elton misreading |
| mr | 0.00418 | vocative / social title |
| fairfax | 0.00367 | Jane Fairfax |
| woodhouse | 0.00365 | family name |
| mrs | 0.00352 | social title |
| jane | 0.00308 | Jane Fairfax again |
| hartfield | 0.00280 | house |
| churchill | 0.00263 | Frank Churchill |
| highbury | 0.00223 | village |
| bates | 0.00167 | Miss Bates |
| randalls | 0.00161 | house |

A gazetteer of Highbury. Theme words do not appear.

## austen-persuasion.txt — *Persuasion*

| Term | Score | Note |
| --- | ---: | --- |
| elliot | 0.00881 | family name, including Anne |
| wentworth | 0.00663 | Captain Wentworth |
| anne | 0.00587 | given name |
| musgrove | 0.00385 | Uppercross family |
| russell | 0.00311 | Lady Russell |
| mrs | 0.00283 | title |
| charles | 0.00276 | Charles Musgrove |
| uppercross | 0.00267 | place |
| kellynch | 0.00253 | the let estate |
| captain | 0.00252 | navy rank as social fact |
| lyme | 0.00233 | Lyme Regis |
| benwick, walter, harville, louisa | ~0.002 | the Lyme circle |

`captain` is the first term that is a social institution rather
than a proper name. The navy is the book.

## austen-sense.txt — *Sense and Sensibility*

| Term | Score | Note |
| --- | ---: | --- |
| elinor | 0.01503 | sense; heaviest Austen name |
| marianne | 0.00906 | sensibility |
| dashwood | 0.00545 | family |
| jennings | 0.00494 | Mrs. Jennings |
| mrs | 0.00359 | title |
| willoughby | 0.00325 | the wrong man |
| lucy | 0.00290 | Lucy Steele |
| brandon | 0.00282 | Colonel Brandon |
| ferrars | 0.00265 | Edward's family |
| barton | 0.00217 | cottage |

Elinor's weight is the largest Austen number on the shelf. The
novel says her name often in a mid-length file.

## bible-kjv.txt — King James Bible

| Term | Score | Note |
| --- | ---: | --- |
| unto | 0.01204 | translation preposition |
| israel | 0.00400 | nation / people |
| saith | 0.00338 | attribution verb |
| thee | 0.00229 | corridor |
| david | 0.00221 | king |
| judah | 0.00217 | nation |
| thou | 0.00217 | corridor |
| hath | 0.00191 | Early Modern verb |
| lord | 0.00174 | divine title; more shared, so lower |
| jesus | 0.00153 | NT; below David because OT volume |

Style first, canon second. `lord` is thematically central and
statistically shared.

## blake-poems.txt — Blake

| Term | Score | Note |
| --- | ---: | --- |
| thel | 0.00558 | *The Book of Thel* |
| weep | 0.00396 | Songs register |
| lyca | 0.00298 | Little Girl Lost / Found |
| thee | 0.00266 | corridor |
| vales | 0.00174 | pastoral |
| oer | 0.00170 | smashed *o'er* |
| har | 0.00149 | *Tiriel* / *Thel* figure |
| thou | 0.00147 | corridor |
| lamb | 0.00146 | Songs of Innocence |
| weeping, infant, morn, joy, worm | ~0.001 | Innocence / Experience nouns |

A pamphlet of named poems, so `thel` and `lyca` behave like novel
heroines. `weep` is the rare content-verb win.

## bryant-stories.txt — Bryant stories

| Term | Score | Note |
| --- | ---: | --- |
| margery, jackal, brahmin, epaminondas | 0.0037–0.0020 | per-story names |
| nightingale, halfchick, tailor, alligator | ~0.0015 | tale vocabulary |
| david | 0.00143 | scripture-adjacent tale (leaks toward KJV) |
| gingerbread, elsa, fir, fox | ~0.001 | more tale nouns |

A collection: no Burgess-level spike. `david` is why a Bible query
has Bryant in second place.

## burgess-busterbrown.txt — Buster Bear

| Term | Score | Note |
| --- | ---: | --- |
| buster | 0.04035 | **heaviest term on the entire shelf** |
| browns | 0.01093 | "Buster Brown's"? / family form |
| joe | 0.01022 | Joe Otter |
| blacky | 0.00927 | Blacky the Crow |
| billy | 0.00709 | Billy Mink |
| otter, sammy, chatterer, trout, mink, jay | 0.005–0.004 | the Green Forest cast |
| farmer, berries, pail, reddy | ~0.004 | plot props |

Children's serial naming. See the length note.

## carroll-alice.txt — Alice

| Term | Score | Note |
| --- | ---: | --- |
| alice | 0.02596 | title; `df = 3` |
| gryphon | 0.00455 | Mock Turtle scene |
| dormouse | 0.00424 | tea party |
| duchess | 0.00424 | |
| hatter | 0.00371 | |
| turtle | 0.00317 | Mock Turtle |
| caterpillar | 0.00182 | |
| rabbit | 0.00178 | more shared, so lower than gryphon |
| herself | 0.00127 | free-indirect / self-talk |
| soup, mouse, hare, dodo | ~0.001 | scenes |

`rabbit` is the book's icon and only the eighth term, because other
files may mention rabbits. `gryphon` does not.

## chesterton-ball.txt — *The Ball and the Cross*

| Term | Score | Note |
| --- | ---: | --- |
| turnbull | 0.01795 | atheist journalist |
| macian | 0.01462 | Catholic Highlander |
| evan | 0.00460 | MacIan's given name |
| turnbulls | 0.00128 | possessive leftover |
| ebook | 0.00096 | **Gutenberg trailer** |
| police | 0.00088 | the novel's running gag |
| madeleine | 0.00085 | |
| highlander | 0.00081 | |
| gutenberg | 0.00074 | **trailer** |
| ebooks | 0.00060 | **trailer** |

Drop the three trailer rows before quoting this list as criticism.

## chesterton-brown.txt — Father Brown

| Term | Score | Note |
| --- | ---: | --- |
| flambeau | 0.00489 | recurring thief / foil |
| boulnois, muscari, fanshaw | 0.0019–0.0013 | one-story names |
| brown | 0.00125 | the priest; the word is shared |
| hirsch, seymour, todhunter, cutler | ~0.001 | more one-story names |
| priest | 0.00106 | office, not name |

Collection physics: the foil outranks the title character because
`brown` is a common English word.

## chesterton-thursday.txt — *The Man Who Was Thursday*

| Term | Score | Note |
| --- | ---: | --- |
| syme | 0.02435 | the poet-detective |
| gregory | 0.00391 | the real anarchist |
| professor, marquis, secretary | 0.0032–0.0020 | council aliases |
| gogol | 0.00175 | |
| anarchists / anarchist | ~0.0016 | the subject word, finally |
| president, bull, ratcliffe | ~0.0014 | more aliases |

`anarchist` is the first abstract noun that describes the book.

## edgeworth-parents.txt — *The Parent's Assistant*

| Term | Score | Note |
| --- | ---: | --- |
| cecilia, susan, piedro, jem, leonora | 0.0027–0.0018 | per-tale children |
| archer, hal, francisco, rory, talbot | ~0.0015 | more tale casts |
| mr, mrs | 0.0016 / 0.0015 | manners titles (Austen glue) |

No term breaks 0.003. That flatness is why cosine can see the
shared moral-novel layer.

## melville-moby_dick.txt — *Moby-Dick*

| Term | Score | Note |
| --- | ---: | --- |
| whale | 0.00494 | content word, `df = 6` |
| ahab | 0.00432 | |
| sperm | 0.00326 | sperm whale |
| stubb | 0.00310 | |
| queequeg | 0.00288 | |
| whales | 0.00276 | plural still thematic |
| starbuck | 0.00230 | |
| pequod | 0.00165 | the ship |
| nantucket | 0.00130 | place |
| boats, whaling, moby, captain, deck, whalemen | 0.0013–0.0009 | industry |

The only novel on the shelf whose #1 term is the subject rather
than a person.

## milton-paradise.txt — *Paradise Lost*

| Term | Score | Note |
| --- | ---: | --- |
| thee | 0.00220 | corridor; not Satan |
| thou | 0.00176 | |
| heaven | 0.00144 | |
| thy | 0.00130 | |
| eve | 0.00116 | |
| th | 0.00114 | smashed *th'* |
| adam | 0.00111 | |
| hath | 0.00098 | |
| spake | 0.00085 | |
| satan | 0.00082 | below Eve and Adam |

Address outranks the adversary. A name query still finds the poem.

## shakespeare-caesar.txt — *Julius Caesar*

| Term | Score | Note |
| --- | ---: | --- |
| bru | 0.02082 | prefix |
| brutus | 0.01666 | |
| cassi | 0.01456 | prefix |
| haue | 0.01240 | Folio *have* |
| cassius | 0.01157 | |
| antony | 0.00776 | |
| caesar | 0.00725 | |
| caes, vs, brut, heere, caska, vpon | 0.005–0.004 | prefixes + Folio |

Cast + compositor.

## shakespeare-hamlet.txt — *Hamlet*

| Term | Score | Note |
| --- | ---: | --- |
| ham | 0.01408 | prefix |
| haue | 0.01022 | Folio |
| hor | 0.00681 | Horatio prefix |
| qu | 0.00584 | Queen |
| laer | 0.00566 | Laertes |
| ophe | 0.00528 | Ophelia |
| pol | 0.00462 | Polonius |
| rosin | 0.00405 | Rosencrantz |
| selfe, loue, horatio, vs, hamlet | 0.0039–0.0036 | Folio + names |

The ghost is absent from the top fifteen. Prefixes ate the list.

## shakespeare-macbeth.txt — *Macbeth*

| Term | Score | Note |
| --- | ---: | --- |
| macb | 0.02156 | prefix |
| haue | 0.01190 | Folio |
| macbeth | 0.00976 | |
| macd | 0.00913 | Macduff prefix |
| rosse | 0.00771 | |
| vpon | 0.00566 | Folio |
| vs | 0.00536 | Folio |
| banquo | 0.00535 | |
| lenox | 0.00441 | |
| mal, thane, banq, doe, feare, cawdor | 0.0039–0.0033 | plot nouns start here |

`thane` and `cawdor` are the first terms that are the play rather
than the printing.

## whitman-leaves.txt — *Leaves of Grass*

| Term | Score | Note |
| --- | ---: | --- |
| o | 0.00183 | vocative / line start; `idf` only 0.405 |
| thee | 0.00099 | corridor |
| poems | 0.00085 | the book talking about itself |
| pioneers | 0.00077 | |
| states | 0.00077 | |
| passd | 0.00076 | smashed *pass'd* |
| chant, cities, forever, soul | ~0.0006 | catalogue register |
| manhattan, america | ~0.0006 | place |

Lowest top-term on the shelf. A wide, shared, chanting vocabulary.
That is also why Whitman is a hub: many weak edges, no spike.
