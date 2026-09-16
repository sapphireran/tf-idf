# TF-IDF as this repo computes it

TF-IDF is a bag-of-words weight. It is large when a term is common **inside one
document** and rare **across the rest of the corpus**. It is a ranking feature,
not a probability and not a linguistic analysis of meaning.

This file is the algebra. For a four-sentence corpus with every intermediate
number filled in, use [`../examples/hand-calculation.md`](../examples/hand-calculation.md).
For how the Perl scripts implement these formulas, use [`pipeline.md`](pipeline.md).

## 1. Term frequency (TF)

After tokenization (see [`tokenizer-and-quirks.md`](tokenizer-and-quirks.md)),
document `d` is a sequence of tokens. Let `count(t, d)` be how many of those
tokens equal `t`, and let `tokens(d)` be the length of the sequence.

This repo uses **relative term frequency**:

```
tf(t, d) = count(t, d) / tokens(d)
```

Properties that follow from that choice:

- `0 ≤ tf(t, d) ≤ 1`
- Summing `tf(t, d)` over every distinct term in `d` equals `1` (empty tokens
  are dropped from the count table but can still inflate `tokens(d)`; see the
  quirks note).
- A word that appears twice in a 20-token document scores `0.1`, the same as a
  word that appears 200 times in a 2,000-token document. Document length is
  already divided out. There is no extra cosine / L2 step later.

`tf-idf-values.pl` writes one `output/tf/<filename>` TSV with
`term<TAB>tf` for every term that occurred at least once.

### Variants this repo does not use

| Variant | Formula | Why people use it |
| --- | --- | --- |
| Raw count | `count(t, d)` | Simple; longer documents dominate |
| Boolean TF | `1` if present | Ignores repetition |
| Log TF | `1 + log(count)` if count > 0 | Dampens “the word appears 400 times” |
| Augmented TF | `0.5 + 0.5 * count / max_count` | Caps the influence of the most frequent term |

The Gutenberg tables are raw relative TF only.

## 2. Document frequency (DF)

```
df(t) = |{ d ∈ corpus : count(t, d) > 0 }|
```

DF is **not** the total number of occurrences. `whale` can appear hundreds of
times in *Moby-Dick* and still have `df = 6` if six files mention it at least
once.

`output/df.txt` stores that count plus the filenames:

```
word <TAB> #docs it exists in <TAB> doc names
whale	6	melville-moby_dick.txt, bible-kjv.txt, ...
```

The filename list is an unordered hash-key dump. Do not treat the order as
ranked importance.

## 3. Inverse document frequency (IDF)

```
idf(t) = ln( N / df(t) )
```

`log` in Perl is the natural logarithm (base *e*), the same as `math.log` in
Python. The checked-in Gutenberg tables use `N = 18`.

| `df(t)` | `idf(t) = ln(18 / df)` | Reading |
| ---: | ---: | --- |
| 1 | `ln(18) ≈ 2.89037` | Term is unique to one file |
| 2 | `ln(9) ≈ 2.19722` | Two files |
| 3 | `ln(6) ≈ 1.79176` | Three files |
| 6 | `ln(3) ≈ 1.09861` | One third of the corpus |
| 9 | `ln(2) ≈ 0.69315` | Half the corpus |
| 18 | `ln(1) = 0` | Every file; weight is wiped out |

IDF is a property of the **corpus**, not of a single document. That is why
`output/idf.txt` is one file shared by every later TF-IDF product.

### Variants this repo does not use

| Variant | Formula | Effect |
| --- | --- | --- |
| Smoothed IDF | `ln(N / (df + 1))` | Avoids `df = 0` if a query term is missing |
| IDF + 1 | `ln(N / df) + 1` | Keeps a floor so no term is exactly zero |
| Probabilistic IDF | `ln((N - df) / df)` | Can go negative for very common terms |
| Base-10 / log2 | `log10` or `log2` | Same ranking within a corpus; different magnitudes |

Because this repo uses unsmoothed `ln(N / df)`:

- A term in every document is exactly `0`.
- A term that somehow had `df = 0` would be undefined (`log` of infinity). The
  scripts never write IDF for terms they never saw.

## 4. TF-IDF

```
tfidf(t, d) = tf(t, d) * idf(t)
```

`tf*idf-product.pl` does that multiplication and writes
`output/tfidf/<filename>`.

Intuition, using numbers from the checked-in tables:

| Term | Document | `tf` (approx) | `df` | `idf` | `tfidf` |
| --- | --- | --- | ---: | ---: | --- |
| `emma` | *Emma* | high | 2 | 2.197 | **0.01043** |
| `harriet` | *Emma* | high | 1 | 2.890 | **0.00713** |
| `the` | *Emma* | very high | 18 | 0 | **0** |
| `whale` | *Moby-Dick* | high | 6 | 1.099 | **0.00494** |
| `ahab` | *Moby-Dick* | lower than `whale` | 2 | 2.197 | **0.00432** |

`whale` is the topical word of *Moby-Dick* but also appears in the Bible,
Whitman, Bryant, and two Shakespeare plays, so IDF pulls it down. `ahab` is
rarer across the corpus (`df = 2`, the other hit is the biblical Ahab), so a
smaller TF still almost catches `whale`.

`harriet` appears only in *Emma*, so it has a larger IDF than `emma` (`emma`
also occurs once in *Persuasion*). Harriet still loses the ranking because Emma
Woodhouse's name is said more often.

## 5. What TF-IDF is good for here

On this Gutenberg sample, TF-IDF is a **character-and-setting finder**:

- Austen novels surface the heroine and her circle.
- *Moby-Dick* surfaces the whale, Ahab, the *Pequod*, and the mates.
- *Alice* surfaces Alice and the set-piece creatures (Gryphon, Dormouse, Hatter).
- Burgess's *Buster Brown* is short and name-heavy, so `buster` scores far above
  anything in the longer novels.

It is a weak **theme** detector. Abstract words (`love`, `death`, `sea`) leak
across books and shrink. It is also sensitive to **edition artifacts**: Folio
speech prefixes, hyphenation that the tokenizer glued together, and leftover
Project Gutenberg headers.

## 6. Ranking, not comparing raw magnitudes across books

TF-IDF as defined here is comparable **within one document** (same `tokens(d)`
and the same IDF table). Comparing a `0.025` in *Alice* to a `0.004` in
*Moby-Dick* is mostly comparing document length and name repetition, not
“Alice-ness vs whale-ness.”

*Alice* is ~26k words; `alice` is repeated constantly. *Moby-Dick* is ~212k
words; even a large raw count is divided by a huge `tokens(d)`.

If you want cross-document comparison, you would usually L2-normalize the
TF-IDF vector of each document. This repo does not do that.

## 7. Worked one-term check

Take `orchard` in the tiny example (`examples/tiny-corpus/docs/apple-orchard.txt`):

- Tokens in that document: `20`
- `count(orchard) = 2` → `tf = 2/20 = 0.1`
- `orchard` appears in 1 of 4 documents → `idf = ln(4/1) = ln(4) ≈ 1.3862943611`
- `tfidf = 0.1 * ln(4) ≈ 0.1386294361`

`apple` has the same TF (`2/20`) but `df = 2`, so `idf = ln(2) ≈ 0.693147`
and `tfidf ≈ 0.069315`. Same in-document frequency, half the weight, because
the city-market document also sells apple tarts.

That contrast — **shared topical words lose to exclusive ones** — is the entire
point of IDF.
