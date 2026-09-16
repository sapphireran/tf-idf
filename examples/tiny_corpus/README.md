# Tiny original corpus

Five short essays written for this lab. They exist so TF-IDF can be
watched on text you can reread in one sitting. They are not Gutenberg
extracts.

| File | Topic | Words the score should surface |
| --- | --- | --- |
| `docs/harbor-cats.txt` | night watch on a pier | cats, tabby, harbor, feline, whiskers |
| `docs/trail-dogs.txt` | a hike with a pack | dogs, leash, trail, canine, fetch |
| `docs/sourdough-baking.txt` | feeding a starter | starter, crust, dough, baking, loaf |
| `docs/winter-constellations.txt` | a backyard telescope | telescope, orion, constellations, nebula |
| `docs/kitchen-garden.txt` | a plot by the oven wall | garden, basil, mint, harvest |

`kitchen-garden.txt` is the bridge document. It mentions the baker,
a visiting dog, and stars on purpose so cosine similarity is not a
block diagonal of unrelated essays.

## Regenerating the committed tables

```bash
python3 examples/python/run_tiny_corpus.py
python3 examples/python/make_report.py --include-worked
```

`expected/summary.txt` is the human-readable ranking. `expected/tf/`,
`expected/idf.txt`, and `expected/tfidf/` use the same tab-separated
shape as the historical `output/` directory.

## What to look at first

1. Open `expected/summary.txt` and confirm each essay's top terms
   match the topic column above. After the latest wording pass,
   `garden`, `cats`, and `dogs` lead their files.
2. Check the cosine table: baking should sit closer to the garden
   than to the winter sky. The garden essay is also close to the
   trail dogs because it mentions a visiting dog on purpose.
3. Open `expected/report.html` in a browser if you want the same
   numbers with the essay text next to them.
4. Flip the formula with `--variant log_tf` or `--variant smooth_idf`
   and watch the rankings move. Those runs should go to a temporary
   directory so they do not overwrite the committed `repo` tables.
