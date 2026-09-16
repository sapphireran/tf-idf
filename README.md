# tf-idf

Personal study copy of a 2012 Gutenberg TF-IDF toy. The original one-line
README said this code accompanies a blog post. The post is gone; the
Perl scripts and the checked-in `output/` tables are still the
calculation that post described.

This checkout adds a **shelf-units** kit: the same `tf * ln(N/df)`
product, recomputed after you change what counts as a document. No
workplace text. No extra Python dependencies.

## Layout

```
tf-idf-values.pl          # 2012: per-file TF, DF, IDF
tf*idf-product.pl         # 2012: TF * IDF
gutenberg/                # 18 public-domain files (NLTK snapshot)
output/                   # fossil tables from that run
shelf_units/              # study-mode library + CLI
examples/commonplace/     # 12 original notes
docs/shelf-units/         # reading path
tests/                    # closed-form + Gutenberg sanity checks
```

## The 2012 grain (one file = one document)

```bash
perl tf-idf-values.pl      # needs a writable output/tf
perl tf*idf-product.pl     # needs Text::CSV_XS
```

Formula encoded by the snapshot:

```
tf  = count / word_count
idf = ln(N / df)           # N = 18 in output/idf.txt
```

Known scars, documented in
[docs/shelf-units/02-reconstructing-the-2012-blog.md](docs/shelf-units/02-reconstructing-the-2012-blog.md):

- the live script sets `$n = $#files` after `readdir` (directory entries,
  not texts)
- hyphens glue tokens (`White-Rabbit` → `whiterabbit`)
- empty `split` fields increment Perl `word_count`

This kit does **not** regenerate `output/`.

## The study grain (you choose the unit)

```bash
python3 -m unittest discover -s tests -v
python3 -m shelf_units demo
```

| Command | Unit of analysis |
| --- | --- |
| `python3 -m shelf_units commonplace` | one personal note |
| `python3 -m shelf_units bible` | one King James book (55 units; minor prophets are bundled) |
| `python3 -m shelf_units chapters carroll-alice` | one Alice chapter |
| `python3 -m shelf_units voices shakespeare-macbeth` | one Folio speaker |
| `python3 -m shelf_units rank "alice rabbit queen" --units gutenberg` | the original 18-file shelf |
| `python3 -m shelf_units passages "hatter twinkle" --file carroll-alice` | an 80-token window |

Measured on this tree (classic cosine, study tokenizer):

- `hypo fixer enlarger` → `01-darkroom` (0.23)
- `zugzwang lucena opposition` → `04-endgame-study` (0.24)
- `hatter hare tea` against Alice chapters → `alice-vii` (0.50), then the trial
- `alice rabbit queen` against the 18 files → `carroll-alice` (0.81)
- `pharaoh egypt passover` against KJV books → `exodus`

## Reading path

Start at [docs/shelf-units/00-index.md](docs/shelf-units/00-index.md).
The argument of the kit is not a new formula. It is that `N` and `df`
encode your filing system, and the 2012 toy filed *Moby-Dick*, the
entire King James text, and *Paradise Lost* each as a single folder
entry.

## License-ish

Gutenberg files are public domain. The Perl scripts are the original
toy. The commonplace notes and the `shelf_units` package were written
for personal study on this checkout.
