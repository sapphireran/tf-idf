# Interpreting the Gutenberg results

The `output/tfidf/` files are alphabetical. The interesting view is
a descending sort that understands scientific notation. All tables
in this page were produced from the checked-in scores with
`examples/rank_terms.py`.

```bash
python3 examples/rank_terms.py output/tfidf/carroll-alice.txt -n 12
```

A high score means: common in this file, uncommon in the other
seventeen. It does not mean "theme of the book" in a literary
sense. Speech prefixes, old spellings, and glued tokens all score
like content words because the tokenizer does not know they are
markup.

## Alice (`carroll-alice.txt`)

2,753 terms. Estimated token count from `tf("alice")` is 26,576,
with `alice` itself occurring 385 times.

| term | TF-IDF | why it ranks |
| --- | ---: | --- |
| alice | 0.025957 | name of the book, df = 3 |
| gryphon | 0.004547 | almost unique to this file |
| dormouse | 0.004242 | same; ties `duchess`, listed first alphabetically |
| duchess | 0.004242 | same |
| hatter | 0.003708 | df = 3; still enough IDF |
| turtle | 0.003169 | Mock Turtle, plus ordinary turtles elsewhere |
| caterpillar | 0.001820 | |
| rabbit | 0.001778 | the White Rabbit; `rabbit` is less rare globally |
| alices | 0.001305 | possessive without an apostrophe |
| herself | 0.001266 | surprisingly high; Alice is the point-of-view magnet |

`wonderland` is only 0.000248. The word barely appears in the
body. The character name does the work that a modern tagger would
assign to the title.

`queen` is only 0.000467 because queens live in Shakespeare,
Chesterton, and the Bible as well, so IDF collapses.

Compare Alice to Moby-Dick when you want "what is Alice-like":

```bash
python3 examples/rank_terms.py output/tfidf/carroll-alice.txt \
    --versus output/tfidf/melville-moby_dick.txt -n 10
```

You should see `alice`, `gryphon`, `dormouse`, `duchess` as absent
or tiny on the Melville side.

## Moby-Dick (`melville-moby_dick.txt`)

19,961 terms. The top of the list is a crew list plus the animal.

| term | TF-IDF | note |
| --- | ---: | --- |
| whale | 0.004943 | df = 6, IDF only 1.099; frequency beats rarity |
| ahab | 0.004322 | df = 2 because 1 Kings has a king Ahab |
| sperm | 0.003258 | sperm whale |
| stubb | 0.003095 | |
| queequeg | 0.002877 | |
| whales | 0.002760 | |
| starbuck | 0.002304 | |
| pequod | 0.001650 | |
| nantucket | 0.001295 | |
| boats | 0.001270 | |

`whale` is the useful reminder that TF-IDF is not "rarest word
wins". Six documents mention a whale. Melville mentions little
else, so the product still peaks there. `ahab` is rarer but not
more frequent, so it comes second.

`moby` is only 0.001077. The title-name is used less often than
the animal.

## Macbeth (`shakespeare-macbeth.txt`)

| term | TF-IDF | note |
| --- | ---: | --- |
| macb | 0.021556 | speech prefix, not a word in the play |
| haue | 0.011900 | Early Modern spelling of *have* |
| macbeth | 0.009755 | the actual name, df = 1 |
| macd | 0.009126 | Macduff's prefix |
| rosse | 0.007710 | Ross, old spelling |
| vpon | 0.005657 | *upon* |
| vs | 0.005365 | *us* |
| banquo | 0.005350 | |
| lenox | 0.004406 | Lennox |
| mal | 0.003934 | Malcolm's prefix; ties `thane` |

The play's "top terms" are mostly **line attributions and
orthography**. That is a correct TF-IDF answer and a bad book
summary. Hamlet has the same shape: `ham`, `hor`, `haue`, `laer`,
`ophe`. If you want character names you have to look past the
prefixes, or pre-process the plays.

`macbeth` itself is still a clean df = 1 signal. No other file in
this folder says the name.

## Emma (`austen-emma.txt`)

| term | TF-IDF |
| --- | ---: |
| emma | 0.010432 |
| harriet | 0.007127 |
| weston | 0.006980 |
| knightley | 0.006140 |
| elton | 0.005793 |
| mr | 0.004177 |
| fairfax | 0.003673 |
| woodhouse | 0.003653 |

This is the ranking people expect from TF-IDF: character names and
the social vocabulary of the novel (`mr`, `mrs`). It works because
the three Austen files are **separate documents**. If you
concatenated *Emma*, *Persuasion*, and *Sense and Sensibility*,
`mr` would lose IDF and the leftover peaks would be the names that
occur in only one novel.

## Blake (`blake-poems.txt`)

Smallest file, so a single repeated name moves the score a lot.

| term | TF-IDF |
| --- | ---: |
| thel | 0.005581 |
| weep | 0.003957 |
| lyca | 0.002976 |
| thee | 0.002662 |
| vales | 0.001742 |
| oer | 0.001697 |
| har | 0.001488 |
| thou | 0.001466 |

`thel` and `lyca` are proper names from *The Book of Thel* and
"The Little Girl Lost". `weep` / `weeping` / `lamb` are the
Innocence lexicon. `thee` and `oer` are period diction that the
novels use less.

## Shared zeros

221 terms have `df = 18` and therefore TF-IDF 0 in every file.
They include the obvious English function words. They also include
a few content words that happen to appear once in every book in
*this* folder. IDF has no opinion about whether a word is
"important to English"; it only knows this directory.

If you added a nineteenth file that never uses `the` (a table of
numbers, a wordlist), `the` would suddenly get a non-zero IDF and
every novel's ranking would change. The score is always relative
to the folder you ran.

## Length and comparison

TF is length-normalized, so a word that takes the same *fraction*
of two books can be compared. The chance of a unique proper name
is not length-normalized. The Bible is 4.3 MB of names; Blake is
38 KB of lyrics. A hapax in Blake is cheaper than a hapax in the
KJV. When you put the two rankings side by side, treat Blake's
decimals as "small book, sharp peaks" and the Bible's as "large
book, flatter mass".

## Quick commands

```bash
# top 15 for any checked-in result
python3 examples/rank_terms.py output/tfidf/austen-emma.txt -n 15

# IDF of a single term
grep -P '^(alice|whale|macbeth)\t' output/idf.txt

# which files contain a term
grep -P '^ahab\t' output/df.txt
```
