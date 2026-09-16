# Three documents, every number

This is the calculator version of `examples/mini_corpus/three_docs/`.
Run the same files with:

```bash
python3 examples/mini_tfidf.py examples/mini_corpus/three_docs
```

The unit tests in `tests/test_mini_tfidf.py` assert these products.

## Tokens

| Document | Text | \( \lvert d \rvert \) |
| --- | --- | ---: |
| `the_harbor.txt` | the whale swims in the harbor | 6 |
| `the_song.txt` | the whale sings a song | 5 |
| `the_bird.txt` | the bird sings a song | 5 |

\(N = 3\). Natural log.

## DF and IDF

\[
\mathrm{idf}(t) = \ln\frac{3}{\mathrm{df}(t)}
\]

| Term | Harbor | Song | Bird | df | IDF |
| --- | :---: | :---: | :---: | ---: | ---: |
| the | ✓ | ✓ | ✓ | 3 | 0 |
| a | | ✓ | ✓ | 2 | ln(3/2) = 0.4054651081081644 |
| whale | ✓ | ✓ | | 2 | 0.4054651081081644 |
| sings | | ✓ | ✓ | 2 | 0.4054651081081644 |
| song | | ✓ | ✓ | 2 | 0.4054651081081644 |
| swims | ✓ | | | 1 | ln 3 = 1.0986122886681098 |
| in | ✓ | | | 1 | 1.0986122886681098 |
| harbor | ✓ | | | 1 | 1.0986122886681098 |
| bird | | | ✓ | 1 | 1.0986122886681098 |

## Harbor TF-IDF

`the` appears twice; everything else once.

| Term | TF | TF-IDF |
| --- | ---: | ---: |
| the | 2/6 = 0.3333333333333333 | 0 |
| whale | 1/6 = 0.16666666666666666 | 0.0675775180180274 |
| swims | 1/6 | 0.18310204811135163 |
| in | 1/6 | 0.18310204811135163 |
| harbor | 1/6 | 0.18310204811135163 |

## Song TF-IDF

| Term | TF | TF-IDF |
| --- | ---: | ---: |
| the | 0.2 | 0 |
| whale | 0.2 | 0.08109302162163288 |
| sings | 0.2 | 0.08109302162163288 |
| a | 0.2 | 0.08109302162163288 |
| song | 0.2 | 0.08109302162163288 |

## Bird TF-IDF

| Term | TF | TF-IDF |
| --- | ---: | ---: |
| the | 0.2 | 0 |
| bird | 0.2 | 0.21972245773362197 |
| sings | 0.2 | 0.08109302162163288 |
| a | 0.2 | 0.08109302162163288 |
| song | 0.2 | 0.08109302162163288 |

`bird` is the largest value in the toy collection: unique term, short
document, TF 20%.

## Cosine similarities

Vectors are aligned on the sorted vocabulary

`a, bird, harbor, in, sings, song, swims, the, whale`.

Zeros omitted in the sketch below:

| Document | Nonzero weights |
| --- | --- |
| harbor | harbor=0.183102, in=0.183102, swims=0.183102, whale=0.067578 |
| song | a=0.081093, sings=0.081093, song=0.081093, whale=0.081093 |
| bird | a=0.081093, bird=0.219722, sings=0.081093, song=0.081093 |

Shared mass:

- harbor ↔ song: only `whale`
- song ↔ bird: `a`, `sings`, `song`
- harbor ↔ bird: nothing

So song and bird are the closest pair, harbor and bird the farthest.
That matches the English: two "sings a song" sentences versus a
sentence about a whale in a harbor.

```bash
python3 examples/cosine_similarity.py --corpus examples/mini_corpus/three_docs
```

Expected order (raw variant):

1. `the_bird.txt` — `the_song.txt` (highest)
2. `the_harbor.txt` — `the_song.txt` (share `whale`)
3. `the_harbor.txt` — `the_bird.txt` (near 0)

Exact floats are asserted in `tests/test_mini_tfidf.py`.

## What changes under `--variant smooth`

Smoothed IDF is \(\ln((N+1)/(\mathrm{df}+1)) + 1\). `the` is no longer
zero:

\[
\ln(4/4) + 1 = 1
\]

and its harbor weight becomes \(1/3 \times 1 \approx 0.333\), which
would *dominate* the harbor ranking. That is the teaching point:
smoothing without a stopword list can put function words back on top.
Raw IDF is harsher and, on this particular toy, more readable.
