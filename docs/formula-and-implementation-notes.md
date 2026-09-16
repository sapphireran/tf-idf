# Formula and implementation notes

The README and the explained-math note describe the **intended** experiment: 18 books, \(\mathrm{idf}(t)=\ln(N/\mathrm{df}(t))\) with \(N=18\). The committed `output/` tables match that story. This page records where the 2012 Perl source, a modern rerun, and those tables disagree.

None of these are security issues. They are the kind of off-by-one and tokenizer nits you want written down before you treat `output/idf.txt` as ground truth.

## 1. \(N\) in the Perl script is `$#files`, not 18

`tf-idf-values.pl` sets

```perl
my $n = $#files;
```

after `readdir(DIR)` on `gutenberg/`. In Perl, `$#files` is the **last index**, not `scalar(@files)`.

`readdir` also returns `.` and `..`. Today the directory also has `.DS_Store`. So a current checkout sees:

| Entry | Tokenized? | Counted in `@files`? |
| --- | --- | --- |
| `.` | no (`/^\./`) | yes |
| `..` | no | yes |
| `.DS_Store` | no | yes |
| 18 `*.txt` books | yes | yes |

That is 21 names, last index **20**. A rerun would compute \(\ln(20/\mathrm{df})\) and would **not** reproduce `output/idf.txt`.

The published hapax IDF is \(\ln 18 = 2.89037175789616\) (`macbeth`, and many numeric tokens). So the committed tables were produced with \(N=18\), i.e. “number of books actually processed”, which is what the 2014 post describes.

The 2012 commit message *“Bugfix: correcting idf values in calculating number of files”* is how `$n = $#files` landed in the tree. It is closer than whatever preceded it, but it is still not “count the files we just tokenized”.

**What to do:** treat `output/` as the dataset for the blog numbers. For new numbers, use `examples/python/tfidf_toy.py`, which sets \(N\) to the number of non-dot files it actually reads.

## 2. Empty tokens inflate `$word_count`

The inner loop is:

```perl
foreach my $d (@data)
{
    $word_count++;
    if($d ne "")
    {
        $tf{$d}++;
        $df{$d}{$f}=1;
    }
}
```

`$word_count` goes up for the empty string you get from leading/trailing spaces or a blank line after cleanup. Those empties never enter `%tf`, so every printed `tf` is slightly **smaller** than `count / (count of real tokens)`.

On *Alice* the gap is small (a few blank lines and split leftovers versus ~26k real tokens). The tiny-corpus documents have no empty tokens, so the Python toy and a pencil calculation match there.

`tfidf_toy.py` defaults to **not** counting empties (`--count-empties` restores the Perl denominator).

## 3. `tr/[A-Z]/[a-z]/` is not a character class in the way it looks

```perl
$txt =~ tr/[A-Z]/[a-z]/;
```

`tr///` transliterates individual characters. The brackets are extra characters in the search and replacement lists, not a range delimiter the way they are in `s///`. For ASCII prose this still lowercases `A–Z` to `a–z`, which is why the published tables are lowercase. It is a lucky, conventional Perl idiom, not a robust Unicode fold.

The Python toy uses `str.lower()` on the same ASCII-only Gutenberg files.

## 4. Punctuation stripping glues and splits words

```perl
$txt =~ s/[^a-zA-Z\d\s]//g;
```

Effects you can see in the tables:

| Original | After cleanup | Consequence |
| --- | --- | --- |
| `Alice's` | `alices` | possessive is a new type |
| `I'm`, `I've` | `im`, `ive` | both rank in Alice |
| `soooop` | `soooop` | the Mock Turtle song keeps its extra o's |
| `1865` | `1865` | title-page year is a token |
| `that you` with a missing space in one book | `thatyou` | one garbage type |

There is no hyphenation policy: `waistcoat-pocket` becomes `waistcoatpocket`.

## 5. One corrupt line in `output/idf.txt`

Around the token `thatyou` the committed IDF file has:

```
thatyou	2.89037175789616y
```

A trailing `y` makes that field not a float. `tf*idf-product.pl` will fail to parse that row (it prints `Error:` and skips it). `examples/python/tfidf_toy.py` skips a non-float IDF with a warning if you point it at the committed file; when it *recomputes* from `gutenberg/` it writes a clean value.

`df.txt` / `tfidf/` do not appear to have the same corruption. If you are computing statistics over `idf.txt`, skip rows that do not parse.

## 6. `Text::CSV_XS` is required only for the product script

`tf-idf-values.pl` writes TSV with `print`. `tf*idf-product.pl` reads TSV with `Text::CSV_XS`. A machine that can run the first script may still fail on the second (`Can't locate Text/CSV_XS.pm`). The Python readers do not need that module.

## 7. Hash order in `df.txt` file lists

The list of books on each `df` row is `keys %{ $df{$t} }`. That order is not part of the experiment. Compare books by looking at each book's `tf` or `tfidf` file.

## 8. `.DS_Store` in `gutenberg/` and `output/`

Both directories carry leftover macOS metadata from the original laptop checkout. The Perl tokenizer skips it (`/^\./`). `tfidf_toy.py` skips dotfiles and `.DS_Store` by name. The files are not part of the 18-book corpus.

## 9. Reproducing the committed `tf * idf` values

Approximate match (same ranking, tiny float noise) when you:

- set \(N = 18\)
- use the same regex cleanup
- ignore empty tokens or accept a ~0.1% tf shift
- skip the corrupt `thatyou` IDF row

Exact byte match of `output/` is not a goal. The files were written by Perl 5 on a 2012 Mac, with `print` of native floats and hash-iterated file lists.

## 10. Recommended sources of numbers

| Need | Source |
| --- | --- |
| Cite the blog / this repo's historical result | `output/` |
| Explain the math on a whiteboard | `examples/tiny-corpus/worked-example.md` |
| Rank or compare books today | `examples/python/tfidf_toy.py` then `rank_terms.py` / `similar_docs.py` |
| Debug the 2012 programs | this page plus `docs/pipeline-and-scripts.md` |
