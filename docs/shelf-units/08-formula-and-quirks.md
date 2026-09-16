# Formula sheet and scars

## The product this kit uses

```
tf(t, d) = count(t, d) / max(words(d), 1)
idf(t)   = ln(N / df(t))          # classic, default
         = ln((N+1)/(df+1)) + 1   # -- not the 2012 default; available in code
tfidf    = tf * idf
```

Logs are natural logs, matching Perl `log` and the snapshot's
`2.89037175789616` for `ln(18)`.

A term with `df = N` has classic idf 0. The index drops those weights
rather than storing a column of zeros. Ranking a query that is only
stopwords against a closed shelf therefore returns scores of 0.

`--idf-mode` is not exposed on every CLI command; `TfIdfIndex(...,
idf_mode="smooth")` is the Python hook if you want the sklearn-ish
variant. The study notes and tests stay on classic unless they are
making that contrast.

## Tokenizer scars that show up in rankings

| Input | Stored token | Where it bites |
| --- | --- | --- |
| `White-Rabbit` | `whiterabbit` | Queries must fuse the hyphen too |
| `th'` | `th` | Milton Book I |
| `Forty-two` | `fortytwo` | Alice's trial |
| `vnsex` | `vnsex` | Lady Macbeth; `unsex` will miss |
| `haile` / `hayle` | both kept | Witches; they do not merge |
| leading spaces on a line | extra Perl `word_count` | Only if you use `tokenize_perl` |

Study mode (`tokenize`) and Perl mode (`tokenize_perl`) share the
character class. They disagree about whether a leading empty `split`
field increments the TF denominator. The checked-in `output/tf/` tables
use the Perl denominator.

## The original `N` disagreement

See [02-reconstructing-the-2012-blog.md](02-reconstructing-the-2012-blog.md).
`tf-idf-values.pl` sets `$n = $#files` after `readdir`, which is not
"number of texts". The frozen `output/idf.txt` nevertheless matches
`ln(18/df)` for hapaxes. This kit does not pretend to know which number
the vanished blog announced. New indexes always use `len(documents)`.

## Cosine ranking

Queries are tokenized the same way as documents, weighted with the
**collection** IDF, and compared with cosine. That is why a three-word
query can beat a baggy document: length lives in the TF denominator and
in the cosine norms, not in a BM25 saturation term. There is no BM25 in
this kit. If you want saturation, that is a different notebook.

## What we refuse to do

- No stopword list in the default path. The 2012 scripts did not have
  one. Classic idf already zeros corpus-wide words.
- No stemming. `anemone` will not match `anemones`.
- No regeneration of `output/`. The fossil stays a fossil.
- No workplace text, no product search stack, no service calls.
