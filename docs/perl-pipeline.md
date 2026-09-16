# Perl pipeline

Two scripts, two passes, tab-separated tables in between. Nothing here is a
module. Run them from the repository root so the relative paths resolve.

```
gutenberg/*.txt
        │
        ▼
 tf-idf-values.pl
        │
        ├── output/tf/<book>.txt     tf(t, d) = count / tokens
        ├── output/df.txt            df(t) and filename list
        └── output/idf.txt           ln(N / df(t))
                │
                ▼
     tf*idf-product.pl
                │
                └── output/tfidf/<book>.txt
```

The second script never opens `gutenberg/`. It only multiplies the tables
from pass 1. That is why you can edit a single TF file and rerun pass 2
without retokenizing 2.1 million words.

## Pass 1: `tf-idf-values.pl`

### Tokenization (per line)

For each line of each `gutenberg/` file that does not start with `.`:

1. `chomp` the newline.
2. Collapse horizontal/vertical whitespace to a single space.
3. Lowercase with `tr/[A-Z]/[a-z]/`.
4. Delete every character that is not ASCII letter, digit, or whitespace:
   `s/[^a-zA-Z\d\s]//g`.
5. `split(/ +/, $txt)` on one or more spaces.

There is no Unicode letter class. Accented characters (rare in this corpus)
would be stripped. Em-dashes, apostrophes, and hyphens disappear *without*
inserting a space, which smashes the tokens on either side.

### Counting

```perl
foreach my $d (@data)
{
    $word_count++;          # increments even when $d eq ""
    if($d ne "")
    {
        $tf{$d}++;
        $df{$d}{$f}=1;
    }
}
```

Two consequences:

1. **Empty tokens inflate the TF denominator.** A line that becomes `" "`
   or a split that yields `""` still increases `tokens(d)`. The checked-in
   Alice TF for `alice` is `0.01448675`, which implies a denominator near
   27,473 if the numerator is 398. `wc -w` on the raw file is 26,443. The
   gap is this counter plus punctuation-deletion creating extra fields.
2. **DF is a set of filenames, not a count of hits.** `$df{$d}{$f} = 1`
   means "term `d` was seen in file `f`." Repeating `whale` a thousand
   times in Melville does not raise `df(whale)`.

After each file, pass 1 writes `output/tf/$f` as `term<TAB>tf`, sorted by
term. TF values are raw Perl numbers (`3.76279349789284e-05` is normal).

### IDF and the `N` bug

After all files:

```perl
my $n = $#files;
...
my $idf_val = log($n/($#vals+1));
```

`@files` is a raw `readdir` of `gutenberg/`. That array includes `.`, `..`,
and any `.DS_Store`. `$#files` is the last index, which is `size - 1`.

| What is on disk | `scalar @files` | `$#files` used as N | Unique-term IDF `ln(N/1)` |
| --- | ---: | ---: | ---: |
| 18 books only (ideal) | 18 | 17 | 2.833 |
| 18 books + `.` + `..` | 20 | 19 | 2.944 |
| 18 books + `.` + `..` + `.DS_Store` | 21 | 20 | 2.996 |
| **Checked-in `output/idf.txt`** | — | **18** | **2.89037** |

The committed IDF table is the *correct* `N = 18` (one per `.txt` book).
The committed source does not compute that number. A later checkout that
still has `.DS_Store` will not reproduce `output/idf.txt` if you rerun pass 1.

I am leaving the Perl as the historical blog-post script. The tiny-corpus
Python example counts documents explicitly.

`$#vals+1` *is* the right way to get `df(t)` from the filename hash keys.

### `df.txt` layout

```
word \t #docs it exists in \t doc names
alice	3	chesterton-thursday.txt, carroll-alice.txt, edgeworth-parents.txt,
```

Filenames are hash-key order (not alphabetical). There is a trailing
comma-space after the last name.

## Pass 2: `tf*idf-product.pl`

This script needs `Text::CSV_XS` and treats each TF/IDF line as a
tab-separated row:

```perl
my $csv = Text::CSV_XS->new({sep_char => "\t"});
...
my $val = $cols[1] * $idf{$cols[0]};
```

- Missing IDF keys multiply as `0` (Perl numeric conversion of `undef`).
  That should not happen if pass 2 runs on tables that pass 1 just wrote.
- Parse failures print `Error: ...` and skip the term.
- Output terms are sorted alphabetically, same as pass 1.
- The script never writes a combined matrix. Each book stays in its own
  file, which is why the Python examples re-read a directory of files.

The filename `tf*idf-product.pl` has a literal `*`. Quote it in the shell:

```bash
perl 'tf*idf-product.pl'
```

## What I do not rerun casually

Regenerating `output/` replaces ~18 + 18 + 2 large text files and will drift
from the numbers quoted in `examples/worked-examples.md` unless `N` is
forced to 18. The personal examples treat `output/` as a frozen snapshot.

If I do regenerate, the checklist is:

1. Remove `gutenberg/.DS_Store`.
2. Change `$n = $#files` to the count of non-hidden files, e.g.
   `scalar grep { $_ !~ /^\./ } @files`.
3. Recreate `output/tf/` and `output/tfidf/` so they stay paired with the
   new `idf.txt`.
4. Re-run `python3 examples/top_terms.py --n 10` and update the worked
   examples if the snapshot numbers moved.
