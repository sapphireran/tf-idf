# Tiny corpus: five original documents

A collection small enough to hold in your head. Same formulas as the Gutenberg pipeline (`tf = count / tokens`, `idf = ln(N/df)`, \(N = 5\)), but every document is a short original paragraph written for this repo.

Use this folder when you want to **predict** a ranking before you compute it. Use `gutenberg/` when you want to see the same product on real books.

## The five documents

| File | Theme | Distinctive words you should expect | Shared on purpose |
| --- | --- | --- | --- |
| `documents/tea-garden.txt` | Harvesting tea on a hillside | `slope`, `bush`, `baskets`, `april` | `tea`, `leaves`, `kettle`, `garden` |
| `documents/tea-ceremony.txt` | Serving powdered tea in a room | `bowl`, `ceremony`, `cloth`, `guests`, `packet` | `tea`, `kettle`, `leaves` |
| `documents/harbor-storm.txt` | Boats tied up in a storm | `rope`, `wall`, `harbor`, `boats` | `storm`, `waves`, `wind`, `rain` |
| `documents/lighthouse-night.txt` | Keeper and lamp in the same weather | `keeper`, `lamp`, `spoke`, `glass`, `climb` | `storm`, `waves`, `harbor`, `kettle` |
| `documents/chess-lesson.txt` | King safety and the knight | `king`, `knight`, `opening`, `square`, `file` | `garden` (metaphor), `count` |

Overlaps are the point:

- `tea` has \(\mathrm{df} = 2\), so it cannot outrank a word that appears only in the ceremony (`bowl`) unless its tf is much larger.
- `garden` appears in the tea garden, as a chess metaphor, and in the lighthouse (“garden workers”), so \(\mathrm{df} = 3\) and its idf is only \(\ln(5/3) \approx 0.511\).
- `kettle` shows up in both tea files and the lighthouse stove. Weather words bind the two sea documents.

## Run it

From the repository root, no third-party packages:

```bash
python3 examples/tiny-corpus/compute_tfidf.py
python3 examples/tiny-corpus/compute_tfidf.py --explain tea
python3 examples/tiny-corpus/compute_tfidf.py --stop --no-write
python3 examples/tiny-corpus/compute_tfidf.py --variants --n 5
python3 examples/top_terms.py --path examples/tiny-corpus/output/tfidf --n 8
```

`--docs` and `--out` point at any other folder of `*.txt` files (including the three-sentence set in [../hand-calculation.md](../hand-calculation.md)).

Default output lands in `output/` here, **not** in the Gutenberg `output/` tree.

## Two rankings, same files

### Raw (no stoplist)

\(N = 5\) is small, so a function word that happens to appear in only one file gets \(\mathrm{idf} = \ln 5 \approx 1.609\). That is why `i` is the top term in the chess lesson and `would` ties the harbor’s `rope` / `wall`. The math is correct; the collection is just too small to treat `i` as common.

Snapshot of the first few raw terms (re-run the script to refresh):

| Document | Top raw terms |
| --- | --- |
| chess-lesson | `i`, then a tie of `file` / `king` / `knight` / `opening` / `square` |
| harbor-storm | `rope`, `wall`, `would`, then `harbor` |
| lighthouse-night | `keeper`, `lamp`, `spoke` |
| tea-ceremony | `bowl`, then `ceremony` / `cloth` / `guests` |
| tea-garden | `bush`, `slope`, then `garden` / `baskets` / `tea` |

`--explain tea` on the raw collection:

```text
df:   2 / 5
docs: tea-ceremony.txt, tea-garden.txt
idf_raw:    0.9162907319   ln(N/df)
tea-ceremony.txt   count 3   tf 0.020833   tfidf 0.019089
tea-garden.txt     count 2   tf 0.013333   tfidf 0.012217
```

`bowl` (count 4, \(\mathrm{df} = 1\)) still beats `tea` in the ceremony: uniqueness outweighs the topic word, same pattern as `and` vs `tea` in the hand calculation.

### With `--stop`

A short built-in English stoplist is dropped **before** tf and df are counted. \(N\) is still 5; the vocabulary shrinks (337 → 294 in the current snapshot). Theme words move up because `i` / `would` / `then` / `for` are gone.

| Document | Top stopped terms |
| --- | --- |
| chess-lesson | `file`, `king`, `knight`, `opening`, `square` |
| harbor-storm | `rope`, `wall`, `harbor`, `boats` / `rain` / `waves` / `wind` |
| lighthouse-night | `keeper`, `lamp`, `spoke`, `climb` / `glass` |
| tea-ceremony | `bowl`, `ceremony`, `cloth`, `tea` still in the top eight |
| tea-garden | `bush`, `slope`, `garden`, `baskets`, `tea` |

This is the ranking people expect when they say “tf-idf finds keywords.” It is not a different formula. It is the same formula on a filtered token stream. [docs/idf-variants.md](../../docs/idf-variants.md) shows a third way to get a similar flip: keep the tokens and add `+1` to idf.

## Files the script writes

```text
examples/tiny-corpus/output/
  df.txt
  idf.txt
  tf/<document>.txt
  tfidf/<document>.txt
```

Same columns as the Gutenberg snapshot. `df.txt` lists filenames so you can see why `garden` is not rare.

Checked-in files under `output/` are a raw (no `--stop`) snapshot. `--stop` is print-only unless you pass `--out` somewhere else; do not overwrite the snapshot with a stopped run if you want to keep `diff` useful.

## How this relates to the Perl scripts

| Choice | Perl Gutenberg pipeline | This helper |
| --- | --- | --- |
| \(N\) | `$#files` on a `readdir` that includes `.` and `..` | `len(documents)` |
| Empty tokens in \(\lvert d \rvert\) | counted | omitted |
| Log | `log` (natural) | `math.log` (natural) |
| Smoothing | none | none (unless you read `--variants`) |
| Stoplist | none | optional `--stop` |
| Output path | `output/` at repo root | `examples/tiny-corpus/output/` |

Rankings will not match a Perl run on these five files until you fix \(N\) in the Perl script. That difference is documented in [docs/pipeline.md](../../docs/pipeline.md) on purpose.

## Suggested exercises

1. Predict whether `storm` or `harbor` ranks higher in `harbor-storm.txt`. Then `--explain` both.
2. Add a sixth document that contains `i` and `would`. Re-run without `--stop`. Watch the chess and harbor tables.
3. Pass `--docs` at the three-sentence hand-calculation folder and confirm the floats in [../hand-calculation.md](../hand-calculation.md).
4. Compare `--variants` on `tea`: smoothing should move it up relative to `bowl` the same way it moved `tea` over `and` in the three-document example.
