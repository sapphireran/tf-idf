# Tiny corpus walkthrough

This is the same formula as the Gutenberg snapshot, on 21 tokens.

```
tf(t, d)    = count(t, d) / 7
idf(t)      = ln(3 / df(t))
tfidf(t, d) = tf(t, d) * idf(t)
```

No punctuation, no leading spaces, no empty `split` fields. Clean mode and Perl-compat mode agree.

## 1. Tokenize

`cats.txt`

```
cats sit on mats
cats chase mice
```

| Token | count |
| --- | ---: |
| cats | 2 |
| sit | 1 |
| on | 1 |
| mats | 1 |
| chase | 1 |
| mice | 1 |
| **token_count** | **7** |

`dogs.txt`

| Token | count |
| --- | ---: |
| dogs | 2 |
| sit | 1 |
| on | 1 |
| mats | 1 |
| chase | 1 |
| cats | 1 |
| **token_count** | **7** |

`birds.txt`

| Token | count |
| --- | ---: |
| birds | 2 |
| fly | 1 |
| over | 1 |
| trees | 1 |
| chase | 1 |
| insects | 1 |
| **token_count** | **7** |

## 2. Term frequency

Every document is length 7, so `tf = count / 7`.

| Token | cats.txt | dogs.txt | birds.txt |
| --- | ---: | ---: | ---: |
| cats | 2/7 ≈ 0.285714 | 1/7 ≈ 0.142857 | — |
| dogs | — | 2/7 ≈ 0.285714 | — |
| birds | — | — | 2/7 ≈ 0.285714 |
| sit | 1/7 | 1/7 | — |
| on | 1/7 | 1/7 | — |
| mats | 1/7 | 1/7 | — |
| chase | 1/7 | 1/7 | 1/7 |
| mice | 1/7 | — | — |
| fly | — | — | 1/7 |
| over | — | — | 1/7 |
| trees | — | — | 1/7 |
| insects | — | — | 1/7 |

## 3. Document frequency and IDF

`N = 3`. Natural log.

| Token | df | books | idf | exact value |
| --- | ---: | --- | --- | ---: |
| chase | 3 | cats, dogs, birds | `ln(3/3) = 0` | 0.0 |
| cats | 2 | cats, dogs | `ln(3/2)` | 0.4054651081081644 |
| sit | 2 | cats, dogs | `ln(3/2)` | 0.4054651081081644 |
| on | 2 | cats, dogs | `ln(3/2)` | 0.4054651081081644 |
| mats | 2 | cats, dogs | `ln(3/2)` | 0.4054651081081644 |
| mice | 1 | cats | `ln(3/1)` | 1.0986122886681098 |
| dogs | 1 | dogs | `ln(3)` | 1.0986122886681098 |
| birds | 1 | birds | `ln(3)` | 1.0986122886681098 |
| fly | 1 | birds | `ln(3)` | 1.0986122886681098 |
| over | 1 | birds | `ln(3)` | 1.0986122886681098 |
| trees | 1 | birds | `ln(3)` | 1.0986122886681098 |
| insects | 1 | birds | `ln(3)` | 1.0986122886681098 |

`chase` is in every document. It is this corpus's `the`. After the product step it will be present in every `tfidf` file with weight `0`.

## 4. The product

`tfidf = (count/7) * idf`.

### cats.txt

| Token | count/7 | idf | tf * idf |
| --- | ---: | ---: | ---: |
| mice | 1/7 | ln(3) | **0.15694461266687282** |
| cats | 2/7 | ln(3/2) | **0.11584717374518982** |
| sit, on, mats | 1/7 | ln(3/2) | 0.05792358687259491 |
| chase | 1/7 | 0 | 0.0 |

`mice` wins even though it appears once, because it is unique. `cats` is more frequent inside the file but is shared with `dogs.txt`, so it comes second. That is the same tradeoff as `dormouse` vs `alice` in the Gutenberg snapshot.

### dogs.txt

| Token | count/7 | idf | tf * idf |
| --- | ---: | ---: | ---: |
| dogs | 2/7 | ln(3) | **0.31388922533374564** |
| cats, sit, on, mats | 1/7 | ln(3/2) | 0.05792358687259491 |
| chase | 1/7 | 0 | 0.0 |

`dogs` is both frequent in the file and unique in the corpus, so it dominates.

### birds.txt

| Token | count/7 | idf | tf * idf |
| --- | ---: | ---: | ---: |
| birds | 2/7 | ln(3) | **0.31388922533374564** |
| fly, over, trees, insects | 1/7 | ln(3) | 0.15694461266687282 |
| chase | 1/7 | 0 | 0.0 |

Birds share no positive-weight token with either mammal document.

## 5. Cosine similarity

Only tokens with a non-zero weight in **both** vectors contribute.

### cats.txt · dogs.txt

Shared positive weights: `cats`, `sit`, `on`, `mats`.

```
dot = (2/7)ln(3/2) * (1/7)ln(3/2)     # cats
    + 3 * ((1/7)ln(3/2))^2            # sit, on, mats
    = 5 * ((1/7)ln(3/2))^2
    ≈ 0.0167757
```

```
|cats| = sqrt( (2/7 ln(3/2))^2 + 3*(1/7 ln(3/2))^2 + (1/7 ln(3))^2 )
       ≈ 0.218216
|dogs| = sqrt( (2/7 ln(3))^2 + 4*(1/7 ln(3/2))^2 )
       ≈ 0.336336
cosine ≈ 0.0167757 / (0.218216 * 0.336336)
       ≈ 0.22857179688308324
```

The documents share a setting (`sit on mats`) and a word (`cats`). They do not share a unique animal name at high weight, so the cosine stays modest.

### cats.txt · birds.txt and dogs.txt · birds.txt

The only shared token is `chase`, and `chase` has weight 0. Cosine is **exactly 0**.

That is the blog post's "John sang for Mary" / "John sang for Kendra" example: the one shared word is corpus-wide, so the vectors are orthogonal.

## 6. What to notice

1. **Zero IDF is a stopword list you did not write.** `chase` is a content verb. In this corpus it is still useless.
2. **Unique + frequent beats unique + rare, and unique + rare can beat shared + frequent.** Compare `dogs` (0.314), `mice` (0.157), and `cats` in `cats.txt` (0.116).
3. **Orthogonal does not mean unrelated in English.** Cats and birds both chase things. The geometry only saw the string `chase`.
4. The numbers in `expected/` are these values, not independently rounded figures. `tests/test_tiny_corpus.py` checks them.

## 7. Reproduce

```bash
python3 examples/python/run_pipeline.py \
  --input examples/tiny-corpus/docs \
  --output /tmp/tiny-tfidf

python3 examples/python/rank_terms.py --tfidf-dir /tmp/tiny-tfidf/tfidf --top 6
python3 examples/python/similarity.py --tfidf-dir /tmp/tiny-tfidf/tfidf
```
