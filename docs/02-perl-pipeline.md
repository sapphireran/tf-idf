# Perl pipeline

Two scripts, two jobs. The first one walks `gutenberg/` and writes almost
everything. The second one only multiplies.

## `tf-idf-values.pl`

1. `opendir` / `readdir` on `gutenberg/`.
2. Skip names that match `/^\./` — so `.` and `..` are skipped, **and so is
   `.DS_Store`** (the name starts with a dot). Hidden files still sit in
   `@files` and therefore still affect `$#files`.
3. For each remaining file:
   - `chomp`
   - collapse `[ \h \v ]+` to a single space
   - `tr/[A-Z]/[a-z]/`
   - drop every character that is not `a-z`, digit, or whitespace
   - `split(/ +/)`
   - increment `word_count` for every field; increment `%tf` and `%df` only
     when the field is non-empty
   - write `output/tf/<filename>` as sorted `term<TAB>normalized_tf`
4. After the loop:
   - `$n = $#files` — **last index**, not `scalar @files`
   - write `output/df.txt` (`word`, document count, comma-separated names)
   - write `output/idf.txt` as `term<TAB>log($n / df)`

The 10 September 2012 commit, *“Bugfix: correcting idf values in calculating
number of files”*, rewrote `output/idf.txt` and every `output/tfidf/` file so
that IDF matches **`ln(18 / df)`**. The script on disk still assigns
`$n = $#files`. On this tree `readdir` sees eighteen texts + `.DS_Store` +
`.` + `..` → 21 names → `$#files = 20`. A fresh Perl run would therefore
*not* match gold. The query desk’s default `N` is the count of non-hidden
text files (18).

## `tf*idf-product.pl`

1. Parse `output/idf.txt` with `Text::CSV_XS` (`sep_char => "\t"`).
2. For each `output/tf/<file>` (again skipping `/^\./`):
   - `tfidf = tf * idf{term}`
   - write `output/tfidf/<file>` sorted by term (not by score)

There is no error if a TF term is missing from the IDF map — Perl treats
that as `0`. In a consistent run that should not happen.

## Output shapes

**`output/df.txt`**

```text
word 	 #docs it exists in 	 doc names
alice	3	chesterton-thursday.txt, carroll-alice.txt, edgeworth-parents.txt,
```

The header uses spaces around the tabs. Document names keep a trailing
comma-space.

**`output/idf.txt`**, **`output/tf/*.txt`**, **`output/tfidf/*.txt`**

```text
term<TAB>number
```

No header. Terms sorted lexicographically. Floats are Perl’s default string
form (plenty of digits, occasional scientific notation for tiny TF).

**`output/df-sorted.txt`** exists from the original drop; the scripts do not
regenerate it.

## Running the 2012 pair

```bash
mkdir -p output/tf output/tfidf
perl tf-idf-values.pl
perl 'tf*idf-product.pl'
```

Quote the second filename. The product script needs `Text::CSV_XS`.

To reproduce the *numbers* without fighting `$#files` and `.DS_Store`:

```bash
python3 -m querydesk self-test
```

That rebuilds TF / IDF / TF-IDF from `gutenberg/*.txt` with `N = 18` and
diffs a sample against `output/`.
