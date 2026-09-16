# Shelf-units command card

Run from the repository root. Stdlib Python 3 only.

```bash
python3 -m unittest discover -s tests -v
python3 -m shelf_units demo
```

## Personal notes

```bash
python3 -m shelf_units commonplace -k 5
python3 -m shelf_units commonplace "hypo fixer enlarger"
python3 -m shelf_units rank "zugzwang lucena opposition" --units commonplace
```

## Gutenberg, still at file grain

```bash
python3 -m shelf_units rank "alice rabbit queen" --units gutenberg -k 5
python3 -m shelf_units rank "white whale ahab" --units gutenberg -k 5
```

## Finer filings

```bash
python3 -m shelf_units bible --book exodus -k 8
python3 -m shelf_units compare genesis exodus --units bible
python3 -m shelf_units chapters carroll-alice -k 5
python3 -m shelf_units chapters milton-paradise -k 4
python3 -m shelf_units voices shakespeare-macbeth -k 6
python3 -m shelf_units rank "hatter hare tea" --units chapters --stem carroll-alice
python3 -m shelf_units passages "hatter march hare twinkle" --file carroll-alice -k 3
```

See [measured-walk.md](measured-walk.md) for numbers from this checkout
and [../../docs/shelf-units/00-index.md](../../docs/shelf-units/00-index.md)
for the prose.
