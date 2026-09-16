# Adding texts

You can drop another public-domain `.txt` file into `gutenberg/` and rebuild. Keep this a personal corpus: do not add company documents or copyrighted books.

## 1. Prepare the file

- Use a `.txt` basename that matches the existing style: `author-shorttitle.txt`, lowercase, hyphens, no spaces.
- Prefer UTF-8. The tokenizer strips anything outside `[A-Za-z0-9]` plus whitespace, so smart quotes, em dashes, and accents simply disappear.
- Optional: copy the file to something like `gutenberg/shakespeare-hamlet.clean.txt` after removing speaker prefixes or Gutenberg boilerplate. The scripts treat that as a **new** document, which changes every IDF value. If you want a cleaned *replacement*, swap the original file instead of adding a sibling.

## 2. Create output directories

The scripts assume these exist:

```bash
mkdir -p output/tf output/tfidf
```

## 3. Rebuild both stages

```bash
perl tf-idf-values.pl
perl 'tf*idf-product.pl'
```

Quote the product script name. A bare `perl tf*idf-product.pl` can expand to multiple arguments if another file matches the glob.

Both stages are full-corpus jobs. There is no incremental update. Adding one file recomputes TF for every file (needed for a consistent `word_count` only per file, but the scripts always scan everything) and recomputes DF/IDF for the whole vocabulary.

## 4. Confirm the new file landed

```bash
ls output/tf/<your-file>
ls output/tfidf/<your-file>
perl examples/top-terms.pl --n 15 output/tfidf/<your-file>
perl examples/lookup-term.pl <a-word-you-expect>
```

`df.txt` should list the new basename on every word that appears in it. IDF for words that used to appear in all 18 files (`the`) will no longer be zero if the new file lacks them — and will stay zero if it contains them.

## 5. What changes when N grows

IDF is `ln(N / df)`. After you add a document:

- Words unique to the new file get a large IDF (`ln(N / 1)`).
- Words that were unique to one old file get a slightly larger IDF because `N` grew and `df` stayed 1.
- Words that appear in every file, including the new one, stay at IDF `0`.

The committed snapshot used `N = 18`. See [algorithm.md](algorithm.md#collection-size-n) before you compare a fresh run to `output/idf.txt`.

## Experimenting without touching Gutenberg

Use the toy runner when you want a fourth short document or a different tokenization check:

```text
examples/toy-corpus/*.txt   →   examples/toy-output/
```

```bash
# add examples/toy-corpus/my-note.txt
perl examples/toy-tfidf.pl
perl examples/top-terms.pl --dir examples/toy-output/tfidf --n 10
```

`examples/toy-tfidf.pl` always rebuilds the toy tree from scratch and never writes under `output/`.

## Dependency note

`tf*idf-product.pl` needs `Text::CSV_XS`. If it is not installed:

```bash
cpanm Text::CSV_XS
# or, on Debian/Ubuntu:
# sudo apt-get install libtext-csv-xs-perl
```

The example helpers do not need it. If you only want ranked terms from an **existing** `output/tfidf/` snapshot, skip the product script entirely.
