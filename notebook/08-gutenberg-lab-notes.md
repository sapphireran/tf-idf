# 08 — Gutenberg shelf observations

Qualitative lab notes against the eighteen-file shelf. Numbers in
the tables below are produced by the Python lab, not copied from
`output/`. If they drift after a tokenizer change, that is a cue to
update this page rather than to "fix" the books.

Re-run:

```bash
python3 -m tfidf corpus-stats --corpus gutenberg
python3 -m tfidf top --doc gutenberg/carroll-alice.txt --k 12 --alpha-only
python3 -m tfidf top --doc gutenberg/melville-moby_dick.txt --k 12 --alpha-only
python3 -m tfidf top --doc gutenberg/shakespeare-macbeth.txt --k 12 --alpha-only
python3 -m tfidf rank "white whale ahab" --corpus gutenberg --k 5
python3 -m tfidf rank "alice rabbit queen" --corpus gutenberg --k 5
python3 -m tfidf rank "macbeth witches thane" --corpus gutenberg --k 5
python3 -m tfidf compare "white whale" --corpus gutenberg -k 3
```

## What I expect before looking

- Length: King James Bible at the top, then *Moby-Dick* / *Leaves of
  Grass* / Austen, with Blake and Burgess at the bottom.
- Alice top terms should look like a children's novel (*alice*,
  *gryphon*, *hatter*, *rabbit*) and not like the KJV.
- *Moby-Dick* should surface *whale*, *ahab*, *sperm*, *stubb* —
  not `the`.
- Macbeth without `--alpha-only` still contains the `1murth` family
  from the 2012 tables. With `--alpha-only` I want *macbeth*,
  *macduff*, *banquo*, *witches* or close cousins.
- The three sanity-check queries should put the obvious book first
  under both cosine/classic and BM25. If they do not, stop and
  write down the actual winner before changing formulas.

## Filled-in tables

I fill these after running the commands in this same pass, so the
notebook carries evidence rather than wishes.

### Token counts

<!-- corpus-stats -->

### Distinctive terms

<!-- top-terms -->

### Query ranks

<!-- ranks -->

### Smoothing comparison on `white whale`

<!-- compare -->

## Reading the historical `output/` snapshot

`output/tfidf/melville-moby_dick.txt` already has `whale` and `ahab`
as large-ish weights (`whale ≈ 0.00494`, `ahab ≈ 0.00432` in the
2012 files). `output/tfidf/carroll-alice.txt` has `a` at 0 because
`a` is collection-wide. Those two facts are the whole TF-IDF sermon
in one shelf.

I am not regenerating `output/`. It stays a fossil of the Perl run.
The Python lab is allowed to disagree with it wherever tokenization
or \(N\) handling differs; [03](03-original-perl-walkthrough.md)
lists the known disagreements.
