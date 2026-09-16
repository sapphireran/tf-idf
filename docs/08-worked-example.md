# A three-sentence worked example

The smallest collection that still shows every moving part is three
sentences:

| file | text | tokens |
| --- | --- | --- |
| `mats.txt` | cats sit on mats | `cats sit on mats` |
| `logs.txt` | dogs sit on logs | `dogs sit on logs` |
| `chase.txt` | cats chase dogs | `cats chase dogs` |

`N = 3`. No punctuation, so tokenization is just lowercase split.

Print the same table from code:

```bash
python3 examples/python/worked_example.py
```

## Document frequency

| term | documents | df |
| --- | --- | --- |
| cats | mats, chase | 2 |
| dogs | logs, chase | 2 |
| sit | mats, logs | 2 |
| on | mats, logs | 2 |
| mats | mats | 1 |
| logs | logs | 1 |
| chase | chase | 1 |

## Inverse document frequency

```
idf(t) = ln(3 / df(t))
```

| term | df | idf |
| --- | --- | --- |
| cats, dogs, sit, on | 2 | `ln(1.5) ≈ 0.405465` |
| mats, logs, chase | 1 | `ln(3) ≈ 1.098612` |

Shared verbs and the two animal names are down-weighted. The nouns
that appear in only one sentence keep the full `ln(3)` boost.

## Term frequency

`mats.txt` and `logs.txt` have length 4. `chase.txt` has length 3.
Every term appears once in the document that contains it, so:

| document | tf |
| --- | --- |
| mats.txt, logs.txt | `1 / 4 = 0.25` |
| chase.txt | `1 / 3 ≈ 0.333333` |

## Product for `mats.txt`

| term | tf | idf | tf-idf |
| --- | --- | --- | --- |
| cats | 0.25 | 0.405465 | 0.101366 |
| sit | 0.25 | 0.405465 | 0.101366 |
| on | 0.25 | 0.405465 | 0.101366 |
| mats | 0.25 | 1.098612 | 0.274653 |

`mats` is the distinctive word, even though it has the same TF as
`cats`. That is IDF doing the only work that matters in this example.

## Product for `chase.txt`

| term | tf | idf | tf-idf |
| --- | --- | --- | --- |
| cats | 0.333333 | 0.405465 | 0.135155 |
| chase | 0.333333 | 1.098612 | 0.366204 |
| dogs | 0.333333 | 0.405465 | 0.135155 |

`chase` leads. `cats` and `dogs` tie, which matches the sentence.

## What to notice

- Changing one sentence changes `df` for several terms and therefore
  every IDF in the collection. IDF is not a property of a document.
- Length sits only in TF. If `chase.txt` were padded with filler
  words, `chase` would keep the same IDF and lose TF.
- Cosine similarity between `mats.txt` and `logs.txt` is high because
  they share `sit` and `on` with identical weights. `chase.txt` sits
  between them: it shares one animal with each.

The unit tests in `tests/test_tfidf_lab.py` lock the `mats` row to
`0.25 * ln(3)` so a later formula change cannot silently drift.
