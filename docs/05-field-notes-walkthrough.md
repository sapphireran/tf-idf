# Field notes walkthrough

A four-document shelf you can finish with a pencil, plus a three-line
hand example that is even smaller. Classic weights: `tf = count / word_count`,
`idf = ln(N / df)`, `tfidf = tf × idf`.

The texts live in `examples/field-notes/texts/`. Expected TSV tables (the
same shape as `output/`) live in `examples/field-notes/expected/`.

```bash
python3 -m querydesk field-notes --query "cairn moraine icefall"
```

## The four notes

**glacier-cairn.txt** (`word_count = 23`, 16 types)

```text
Cairn stones mark the glacier moraine above the hut.
A second cairn faces the icefall.
The hut book stays dry under the cairn.
```

**letterpress-proof.txt** (`word_count = 23`, 15 types)

```text
The chase holds the type and the furniture.
Quoins lock the chase against the bed.
A proof from the tympan shows the type.
```

**tide-gauge.txt** (`word_count = 25`, 18 types)

```text
The tide gauge sits in a stilling well by the pier.
Slack water hides the datum on the staff.
The staff reads the tide twice.
```

**herbarium-press.txt** (`word_count = 22`, 16 types)

```text
The press dries the voucher between blotters.
A silica packet keeps the genus label clean.
The voucher stays flat in the press.
```

`N = 4`. Shared glue: `the` and `a` appear in every note, so
`idf = ln(4/4) = 0`. `stays` is in glacier + herbarium (`df = 2`,
`idf = ln 2 ≈ 0.693147`). `in` is in tide + herbarium. Every workshop
noun is a hapax: `idf = ln 4 ≈ 1.386294`.

## Glacier, line by line

Raw counts that matter:

| term | count | tf = count/23 | idf | tfidf |
| --- | ---: | ---: | ---: | ---: |
| cairn | 3 | 0.130435 | 1.386294 | **0.180821** |
| hut | 2 | 0.086957 | 1.386294 | 0.120547 |
| icefall | 1 | 0.043478 | 1.386294 | 0.060274 |
| moraine | 1 | 0.043478 | 1.386294 | 0.060274 |
| glacier | 1 | 0.043478 | 1.386294 | 0.060274 |
| stays | 1 | 0.043478 | 0.693147 | 0.030137 |
| the | 5 | 0.217391 | 0 | 0 |

`cairn` is the heading term because it is both repeated and unique to this
note. `the` is the most frequent token and still contributes nothing.

## Query: `cairn moraine icefall`

The query has three hapax terms, all from the glacier note. Cosine against
the other three notes is **0** (no overlap). Against glacier it is about
**0.586**. Attribution is the product of query TF-IDF and document TF-IDF:

- `cairn` pays the most (query TF 1/3, document TF 3/23, both × `ln 4`)
- `moraine` and `icefall` split the rest (each appears once in the note)

The other themed queries behave the same way:

| Query | Winner | Cosine (approx.) |
| --- | --- | ---: |
| `cairn moraine icefall` | `glacier-cairn.txt` | 0.586 |
| `chase quoins tympan` | `letterpress-proof.txt` | 0.530 |
| `stilling datum slack` | `tide-gauge.txt` | 0.376 |
| `voucher blotters silica` | `herbarium-press.txt` | 0.537 |
| `the` | everyone, score 0 | 0 |

`stilling datum slack` is the weakest of the four hits because those three
terms are each hapaxes that occur only once in a slightly longer note
(25 tokens), so the document vector is more spread out.

## Hand example (three one-line docs)

Keep this next to [01-weights-this-repo-uses.md](01-weights-this-repo-uses.md)
when you want fractions without a 23-token denominator.

| doc | text |
| --- | --- |
| `alpha.txt` | `cairn cairn ice` |
| `beta.txt` | `chase type` |
| `gamma.txt` | `cairn type` |

`N = 3`.

| term | df | idf = ln(3/df) |
| --- | ---: | ---: |
| ice, chase | 1 | ln 3 ≈ 1.098612 |
| cairn, type | 2 | ln(3/2) ≈ 0.405465 |

**alpha** (`word_count = 3`): `tf(cairn) = 2/3`, `tf(ice) = 1/3`

- `tfidf(cairn) = (2/3) × 0.405465 ≈ 0.270310`
- `tfidf(ice) = (1/3) × 1.098612 ≈ 0.366204`

**beta** (`word_count = 2`): `tfidf(chase) ≈ 0.549306`, `tfidf(type) ≈ 0.202733`

**gamma**: `tfidf(cairn) ≈ 0.202733`, `tfidf(type) ≈ 0.202733`

A query `ice` is a one-hot vector on `ice`. Cosine with alpha is 1 after
you ignore the orthogonal `cairn` coordinate in the *query* (the query has
no `cairn`). Dot product is `q_tfidf(ice) × 0.366204`. Beta and gamma
score 0. That is the same isolation you get on the four field notes, with
less arithmetic.

The `unittest` suite rebuilds both this hand example and the four notes
(`tests/test_weights.py`, `tests/test_field_notes.py`).
