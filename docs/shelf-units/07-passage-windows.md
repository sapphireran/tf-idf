# Passage windows

Chapter units still assume a novelist already chose the cuts. Sometimes
you want a query to point at a span. `shelf_units.retrieve` tokenizes a
long string, slides a window, builds a classic TF-IDF index over those
windows, and cosine-ranks the query.

```bash
python3 -m shelf_units passages "hatter march hare twinkle" --file carroll-alice --window 80 --stride 40 -k 3
```

On this checkout that command returns, among others:

| score | span | gist |
| ---: | --- | --- |
| 0.705 | tokens 14400:14480 | the Queen of Hearts concert; `twinkle twinkle little bat` |
| 0.665 | tokens 14440:14520 | the Hatter continues; teatray / dormouse |
| 0.439 | tokens 14360:14440 | "we quarrelled last march—just before he went mad" |

The windows overlap (`stride=40`, `window=80`), so the top two are
neighbors of the same song. That is expected. Tightening the stride
makes a smoother heatmap and a slower index.

## What a window is not

It is not a sentence segmenter. Punctuation is already gone, so the
"text" you print is a token join. It is also not using chapter IDF: each
run builds IDF from the windows themselves. A word that appears in every
window (`alice` in *Alice*) has classic idf 0 and cannot help. A word
that appears in three windows (`twinkle`) becomes a flare.

You can point `--file` at any of the Gutenberg texts or at a commonplace
note. For *Moby-Dick*, start with a wider window (120–160 tokens) or the
hits become a spray of `whale` without enough surrounding sentence to
read.

## File vs chapter vs window

Same query, three grains, *Alice*:

| grain | question answered |
| --- | --- |
| `--units gutenberg` | This book, not *Moby-Dick*. Score for `alice rabbit queen` is 0.808 on `carroll-alice`. |
| `--units chapters --stem carroll-alice` | Chapter VII, then the trial. |
| `passages` | The twinkle song, plus the March quarrel. |

That ladder is the kit. Everything else is commentary.
