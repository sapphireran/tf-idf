# Hand calculation: three tiny documents

This page is a complete numeric walkthrough. No Gutenberg text, no Perl. Every fraction is written out so you can check the Python helper against a scrap of paper.

Collection:

| id | text |
| --- | --- |
| `d1` | `the tea is hot` |
| `d2` | `the storm is loud` |
| `d3` | `hot tea and tea leaves` |

Tokenization does nothing extra here: already lowercase, no punctuation.

## 1. Tokens and raw counts

**d1** (4 tokens): `the` 1, `tea` 1, `is` 1, `hot` 1

**d2** (4 tokens): `the` 1, `storm` 1, `is` 1, `loud` 1

**d3** (5 tokens): `hot` 1, `tea` 2, `and` 1, `leaves` 1

\(N = 3\).

## 2. Normalized tf

\[
\mathrm{tf}(t, d) = \mathrm{count}(t, d) / |d|
\]

| term | d1 | d2 | d3 |
| --- | ---: | ---: | ---: |
| the | \(1/4 = 0.25\) | \(0.25\) | — |
| tea | \(0.25\) | — | \(2/5 = 0.4\) |
| is | \(0.25\) | \(0.25\) | — |
| hot | \(0.25\) | — | \(0.2\) |
| storm | — | \(0.25\) | — |
| loud | — | \(0.25\) | — |
| and | — | — | \(0.2\) |
| leaves | — | — | \(0.2\) |

## 3. Document frequency

A document contributes \(1\) if the term occurs at least once.

| term | documents | df |
| --- | --- | ---: |
| the | d1, d2 | 2 |
| tea | d1, d3 | 2 |
| is | d1, d2 | 2 |
| hot | d1, d3 | 2 |
| storm | d2 | 1 |
| loud | d2 | 1 |
| and | d3 | 1 |
| leaves | d3 | 1 |

## 4. Inverse document frequency

\[
\mathrm{idf}(t) = \ln(N / \mathrm{df}(t))
\]

Using Python’s `math.log` (natural log), rounded to 10 digits after the point:

| df | formula | idf |
| ---: | --- | ---: |
| 2 | \(\ln(3/2) = \ln 1.5\) | `0.4054651081` |
| 1 | \(\ln(3/1) = \ln 3\) | `1.0986122887` |

```python
import math
assert round(math.log(3 / 2), 10) == 0.4054651081
assert round(math.log(3 / 1), 10) == 1.0986122887
```

## 5. tf × idf

Shared terms (\(\mathrm{df} = 2\)) use idf `0.4054651081`. Unique terms use idf `1.0986122887`.

### d1 — every surviving term is shared

| term | tf | idf | tf-idf |
| --- | ---: | ---: | ---: |
| the | 0.25 | 0.4054651081 | **0.1013662770** |
| tea | 0.25 | 0.4054651081 | **0.1013662770** |
| is | 0.25 | 0.4054651081 | **0.1013662770** |
| hot | 0.25 | 0.4054651081 | **0.1013662770** |

d1 is a four-way tie. The document is “about” tea only in English, not in this scoring. Nothing in d1 is collection-rare.

### d2 — two unique weather words

| term | tf | idf | tf-idf |
| --- | ---: | ---: | ---: |
| storm | 0.25 | 1.0986122887 | **0.2746530722** |
| loud | 0.25 | 1.0986122887 | **0.2746530722** |
| the | 0.25 | 0.4054651081 | 0.1013662770 |
| is | 0.25 | 0.4054651081 | 0.1013662770 |

`storm` and `loud` win, clearly. Same tf as `the`; the entire gap is idf.

### d3 — repeated `tea` vs. unique function words

| term | tf | idf | tf-idf |
| --- | ---: | ---: | ---: |
| and | 0.2 | 1.0986122887 | **0.2197224577** |
| leaves | 0.2 | 1.0986122887 | **0.2197224577** |
| tea | 0.4 | 0.4054651081 | **0.1621860432** |
| hot | 0.2 | 0.4054651081 | 0.0810930216 |

This is the important surprise:

- `tea` is the *topic* word and has the highest tf (\(0.4\)).
- `and` and `leaves` still outrank it because they appear in only one document, so their idf is \(\ln 3\) rather than \(\ln 1.5\).
- Check the inequality: \(0.4 \times \ln 1.5 \approx 0.162\) vs. \(0.2 \times \ln 3 \approx 0.220\). Uniqueness beats a 2× tf bump in this collection.

That is why a three-document toy set is a bad keyword extractor and a good formula tutor. Add a stopword list, or grow \(N\) until `and` appears elsewhere, and the ranking starts to match the English topic.

## 6. What would change the ranking

| Change | Effect on d3 |
| --- | --- |
| Add a fourth document that contains `and` | \(\mathrm{df}(\mathtt{and})\) becomes 2; `tea` can overtake it |
| Use \(\mathrm{idf} = \ln(N/\mathrm{df}) + 1\) | Shared terms get a +1 floor; gaps shrink but signs stay |
| Use raw counts instead of normalized tf | d3 `tea` becomes 2 vs. `and` 1; still not enough against \(\ln 3 / \ln 1.5 \approx 2.71\) |
| Stem `leaves` → `leaf` | No change unless another document uses `leaf` / `leaves` |
| Drop tokens in a stoplist `{the,is,and}` | d3 top terms become `leaves`, then `tea` |

## 7. Reproduce with the helper

The tiny-corpus script accepts any directory of `*.txt` files. You can drop these three lines into a temp folder and get the same table:

```bash
mkdir -p /tmp/tfidf-hand/{d1,d2,d3}
# easier: three files in one folder
mkdir -p /tmp/tfidf-hand
printf 'the tea is hot\n' > /tmp/tfidf-hand/d1.txt
printf 'the storm is loud\n' > /tmp/tfidf-hand/d2.txt
printf 'hot tea and tea leaves\n' > /tmp/tfidf-hand/d3.txt
python3 examples/tiny-corpus/compute_tfidf.py --docs /tmp/tfidf-hand --out /tmp/tfidf-hand-out
python3 examples/tiny-corpus/compute_tfidf.py --docs /tmp/tfidf-hand --explain tea
```

The unit tests in `tests/test_tiny_tfidf.py` lock the eight idf values and the d3 ranking to the floats on this page.

## 8. Connecting this page to the Gutenberg snapshot

Same product, larger \(N\):

- Alice’s `gryphon` is d2’s `storm`: almost private to one file, moderate tf, large idf.
- Alice’s `alice` is a stronger version of d3’s `tea`: high tf *and* low df (the name barely appears in the other seventeen files).
- Alice’s `a` / `about` / `after` at score `0` are the limit of d1’s four-way tie: \(\mathrm{df} = N\), so idf is exactly \(0\).

If a Gutenberg ranking ever looks “wrong,” compute \(\mathrm{df}\) first. Most surprises are either \(\mathrm{df} = 1\) on a speaker tag, or \(\mathrm{df} = N\) on a function word.
