# Examples

Personal teaching collections. None of these files are company
documents. The micro set is small enough to compute by hand; the tiny
set is paragraph-length original prose with an obvious three-way split.

## Layout

```
examples/
  micro-corpus/            three one-line documents (cat / dog / bread)
  micro-corpus-expected/   teaching-pipeline TSV for the micro set
  tiny-corpus/             three short original paragraphs
  tiny-corpus-expected/    teaching-pipeline TSV for the tiny set
  sample-rankings/         top-8 listings for the tiny set and Gutenberg
  python/                  stdlib TF-IDF + ranker
  perl/top_terms.pl        rank a TSV without CPAN
```

Hand-computed table for the micro set:
[../docs/worked-example.md](../docs/worked-example.md).

## Micro corpus

```bash
python3 examples/python/compute_tfidf.py \
  --input-dir examples/micro-corpus \
  --output-dir /tmp/micro-tfidf

python3 examples/python/top_terms.py /tmp/micro-tfidf/tfidf --top 5
```

Expected ranking shape:

- `d1-cat.txt`: `cat` and `mat` tied at the top
- `d2-dog.txt`: `dog` and `log` tied at the top
- `d3-bread.txt`: `bake`, `bakers`, `bread` tied (short document, all `df = 1`)

## Tiny corpus

Three original paragraphs written for this repo so the distinctive
terms are obvious without being a single repeated word.

```bash
python3 examples/python/compute_tfidf.py \
  --input-dir examples/tiny-corpus \
  --output-dir /tmp/tiny-tfidf

python3 examples/python/top_terms.py /tmp/tiny-tfidf/tfidf --top 8
```

Expected distinctive terms:

| Document | Should rank high | Should not rank high |
| --- | --- | --- |
| `cats.txt` | cats, cat, purr, yarn, sofa, whiskers | bread, ovens, bark |
| `dogs.txt` | dogs, dog, bark, ball, garden, ears | bread, yarn, whiskers |
| `baking.txt` | bread, dough, flour, ovens, baker | cats, dogs, yarn |

Cats and dogs share sofa-adjacent language (`sun`, `nap`, `soft`,
`fur`, `afternoon`) on purpose. Those shared tokens get a lower IDF
and fall behind the animal-specific words. Baking shares almost
nothing with the other two, so its kitchen vocabulary stays loud.

## Rank the Gutenberg snapshot

```bash
python3 examples/python/top_terms.py output/tfidf --top 10
perl examples/perl/top_terms.pl output/tfidf/melville-moby_dick.txt 12
```

Reading those lists: [../docs/interpreting-results.md](../docs/interpreting-results.md).

## Tests

```bash
python3 -m unittest discover -s tests -v
```
