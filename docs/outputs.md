# Output formats

All generated tables are UTF-8 (in practice ASCII) text with **tab** separators and **no quoting**. The Gutenberg snapshot lives under `output/`. The toy runner writes the same shape under `examples/toy-output/`.

## Directories

| Path | Produced by | Contents |
| --- | --- | --- |
| `output/tf/<name>.txt` | `tf-idf-values.pl` | Normalized TF for one document |
| `output/idf.txt` | `tf-idf-values.pl` | Collection IDF |
| `output/df.txt` | `tf-idf-values.pl` | Document frequency plus file names |
| `output/df-sorted.txt` | original experiment | DF table in a scan-friendly order |
| `output/tfidf/<name>.txt` | `tf*idf-product.pl` | TF × IDF for one document |

`<name>.txt` matches the basename in `gutenberg/`. The scripts do not create `output/tf/` or `output/tfidf/` themselves; create those directories before the first run.

## `output/tf/<file>`

```text
<token>\t<tf>
```

- One row per distinct token in that document.
- Rows sorted by token (`sort keys %tf`).
- `<tf>` is `count / word_count` as a Perl number (`0.0235927152317881`).
- Tokens that never occur in the file are omitted (no explicit zeros).

Example from `output/tf/carroll-alice.txt`:

```text
1865	3.76279349789284e-05
a	0.0235927152317881
alice	0.0144866475138874
```

## `output/idf.txt`

```text
<token>\t<idf>
```

- One row per token that occurred in at least one processed file.
- Rows sorted by token.
- `<idf>` is `ln(N / df)`. Common words that hit `df = N` are stored as `0`.

```text
alice	1.79175946922805
and	0
the	0
whale	1.09861228866811
```

## `output/df.txt`

```text
word \t #docs it exists in \t doc names
<token>\t<df>\t<file>, <file>, ...
```

The first line is a human header, including spaces around the tabs. Data rows list file names in hash-key order (not alphabetical) and leave a trailing `, ` after the last name.

```text
alice	3	carroll-alice.txt, chesterton-thursday.txt, bryant-stories.txt,
```

`output/df-sorted.txt` is the same information rearranged for browsing. The scripts do not regenerate it.

## `output/tfidf/<file>`

```text
<token>\t<tfidf>
```

Same row order as the TF table (sorted by token, **not** by score). A zero usually means IDF was zero, not that the word is absent — absent words are omitted.

```text
a	0
alice	0.0259568
about	0
```

Rank with:

```bash
perl examples/top-terms.pl --n 20 output/tfidf/melville-moby_dick.txt
```

## Parsing rules

- Split on the first tab only if you need to be defensive; tokens themselves contain no tabs because punctuation was stripped.
- Do not use a CSV parser that treats `#` as a comment; `df.txt` is not `#`-commented, but some tokens start with digits.
- `tf*idf-product.pl` uses `Text::CSV_XS` with `sep_char => "\t"`. The helpers under `examples/` split on `\t` in core Perl so they run without that module.
- Scientific notation (`8.26770235301107e-05`) is valid input for `lookup-term.pl` and `top-terms.pl`.

## Fresh run vs committed snapshot

A new `perl tf-idf-values.pl` overwrites `output/tf/`, `output/df.txt`, and `output/idf.txt`. A new `perl 'tf*idf-product.pl'` overwrites `output/tfidf/`. If `N` differs from the snapshot (see [algorithm.md](algorithm.md#collection-size-n)), every IDF and TF-IDF value changes even when the corpus is unchanged.

The toy example writes under `examples/toy-output/` so Gutenberg snapshot files stay intact.
