# Reconstructing the 2012 blog from the repo

The commit message on `a170430` points at

`http://nlp-stuff.blogspot.com/2012/09/tfidf-example-and-implementation-details.html`

That URL is gone. The repository is still here, so the blog can be
reconstructed from the scripts it shipped.

## What the toy was

Two Perl programs and a folder of Project Gutenberg texts, originally
bundled with NLTK's `gutenberg` corpus:

1. `tf-idf-values.pl` walks `gutenberg/`, writes per-file term frequencies
   into `output/tf/`, a document-frequency table into `output/df.txt`, and
   inverse document frequencies into `output/idf.txt`.
2. `tf*idf-product.pl` multiplies those two tables into `output/tfidf/`.

The product is the classical one, not BM25, not sublinear TF, not a
smoothed sklearn vectorizer.

## How a line becomes tokens

For each physical line the first script:

1. `chomp`s the newline
2. collapses `[\\h\\v]+` to a single space
3. lowercases with `tr/[A-Z]/[a-z]/`
4. deletes `[^a-zA-Z\\d\\s]`
5. `split(/ +/)`

Then it increments `$word_count` for **every** split field, including a
leading empty field, and only then skips empty keys when filling `%tf`.
That is why a line that starts with a space contributes to the
denominator without contributing a token. Study mode in
`shelf_units.tokenize.tokenize` keeps the same character class and drops
the empty fields from the count. Use `tokenize_perl` if you are trying to
line up with a cell in `output/tf/`.

Punctuation is glue, not a boundary. `White-Rabbit` becomes `whiterabbit`.
`Forty-two` becomes `fortytwo`. Folio `haile` stays `haile`. The snapshot
is full of those fused tokens; they are not bugs in the output, they are
the tokenizer.

## The `N` quirk

After `readdir`, the script sets

```perl
my $n = $#files;
```

`@files` includes `.` and `..`. With 18 books that array has 20 entries,
so `$#files` is 19. The 2012-09-10 commit message says the author "corrected
idf values in calculating number of files"; the correction still counts
directory entries, not documents. The checked-in `output/idf.txt` is
therefore `ln(19/df)` for a one-document term (`≈ 2.944`) rather than
`ln(18/df)` (`≈ 2.890`) — except the file on disk actually shows
`2.89037175789616` for hapax-like tokens such as `00`, which is `ln(18)`.

So the live script and the frozen tables do not agree about `N`. This kit
does not try to launder that. When it talks about the snapshot it uses
`N = 18` because that is what `output/idf.txt` encodes. When it talks
about a new unit set it uses the true unit count (12 Alice chapters, 55
Bible units, 12 commonplace notes).

## What the frozen tables are good for

They are a fossil of one run. They are not a gold standard for "the"
TF-IDF of these books. Terms that appear in all 18 files have idf 0 and
print as `0` in `output/tfidf/` — that is why `a` / `the` / `and` look
like they vanished. Rare OCR crumbs (`00021053` in *Paradise Lost*) get
the full hapax weight and then almost no TF, so they rarely win a ranking.

If you want to rerun the Perl, you need `Text::CSV_XS` for the second
script. This kit never calls those programs. It leaves them as the blog
artifact and recomputes on purpose-built units instead.

## A one-screen map of the original pipeline

```
gutenberg/*.txt
        │
        ▼
tf-idf-values.pl
        │
        ├── output/tf/<file>      term<TAB>count/word_count
        ├── output/df.txt         term<TAB>df<TAB>file, file, …
        └── output/idf.txt        term<TAB>ln(N/df)
                │
                ▼
        tf*idf-product.pl
                │
                └── output/tfidf/<file>   term<TAB>tf*idf
```

Everything in `docs/shelf-units/` after this page is what you can see
once you stop treating those 18 files as the only legal documents.
