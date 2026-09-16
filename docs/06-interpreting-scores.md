# How to read a score

A TF-IDF value in this repo is not a probability and not a percentage.
It is a product of a small proportion and a log ratio. Comparing two
terms *inside one document* is the intended use. Comparing a term in
*Alice* to a term in *Moby-Dick* is only fair after you remember that
the novels have very different lengths.

## Read down a single file first

Take the committed top of `output/tfidf/carroll-alice.txt`:

| term | tf-idf | how to read it |
| --- | --- | --- |
| `alice` | 0.0260 | the book's own name, rare elsewhere |
| `gryphon` | 0.0045 | invented creature, almost collection-unique |
| `dormouse` | 0.0042 | same |
| `duchess` | 0.0042 | character title with low df |
| `hatter` | 0.0037 | same |
| `herself` | 0.0013 | a reminder that pronouns are not stopped |

`alice` wins because it is repeated constantly *and* almost absent
from the other seventeen books. `herself` is a useful warning: IDF
only knows document spread, not part of speech. A pronoun that happens
to be rarer in this mixed collection can still surface.

## Collection-unique terms look "large"

Any term with `df = 1` gets `idf = ln(18) ≈ 2.890`. Its TF-IDF is then
just `2.890 * (count / |d|)`. That is why a word that appears a
handful of times in a short file (Blake) can outscore a word that
appears hundreds of times in a long file (Melville). Length is in the
denominator of TF.

## Zero is a real answer

Common words such as `a` and `about` have TF-IDF `0` in
`carroll-alice.txt` because they appear in every book. The TF column
is still positive; the IDF column is zero. If a term you expected to
be distinctive scores zero, check `output/df.txt` before changing the
tokenizer. The word is probably just widely shared.

## Speech prefixes and archaic spelling

Hamlet's table is dominated by `ham`, `haue`, `hor`, `qu`, `laer`.
Those are editorial artifacts:

- `ham` is the speaker tag for Hamlet
- `haue` is an old spelling of *have*
- `hor` and `laer` are Horatio and Laertes tags
- `selfe` and `loue` are the same story: `e` where modern English
  has dropped it

If you want topical words instead of tags, strip speaker prefixes
before tokenization. This lab leaves them in so the committed tables
stay honest about the input.

## Use the tiny corpus when you want less noise

The five original essays were written so the top terms are the topic:

- harbor cats → `cats`, `tabby`, `harbor`, `feline`
- trail dogs → `dogs`, `leash`, `trail`
- sourdough → `starter`, `crust`, `dough`
- winter sky → `telescope`, `orion`, `constellations`
- kitchen garden → `garden`, `mint`, `basil`

Cosine similarity on those five files also behaves intuitively:
baking is closer to the kitchen garden than to the winter sky,
because they share `oven` / cook / crumb vocabulary and the garden
essay mentions the baker on purpose.
