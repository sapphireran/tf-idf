# Quirks

The 2012 scripts are short. Most surprises in the gold tables come from
four implementation details, not from the math.

## 1. `N` is not `scalar @files`

```perl
my $n = $#files;                 # last index
my $idf_val = log($n/($#vals+1));
```

`readdir` includes `.` and `..`. This tree also has `gutenberg/.DS_Store`.
That is 21 names and `$#files = 20`. The **checked-in** IDF file uses
`N = 18` (the 10 September 2012 bugfix rewrote the numbers; it did not
change this line).

The desk defaults to `--n-mode texts` (`N` = count of non-hidden `*.txt`).
`--n-mode perl-last-index` rebuilds IDF the way a naive rerun of the Perl
would.

## 2. Hidden files are skipped as documents, kept in `@files`

`if ($f !~ /^\./)` skips `.DS_Store` for TF, so it never becomes a
nineteenth document. It still occupies a slot in `@files`. You cannot see
that in `output/df.txt`; you only see it if you rerun the script.

## 3. Empty split fields inflate `word_count`

After whitespace collapse, a line that still starts with a space produces
a leading empty field. The loop always does `$word_count++` and only then
asks `if ($d ne "")`. TF is therefore slightly smaller than
`count / (count of real tokens)` on files with indented verse (Blake,
Milton, Shakespeare).

The Alice gold table matches this rule to `~1e-16`. The desk tokenizer is
tested against that file.

## 4. Punctuation is deleted, not turned into a break you already had

`Alice's` becomes `alices`. `o'er` becomes `oer`. `Mr.` becomes `mr`.
There is no stemmer and no possessives list. That is why Alice’s own
heading list includes `alices` as a hapax.

## 5. Folio orthography is a feature

The three Shakespeare files keep First Folio spellings. `haue`, `vpon`,
and `vs` occur in all three plays (`df = 3`, idf `1.7918`) and nowhere
else, so they behave like a **genre tag** for the folio trio. They are not
errors in the TF-IDF math.

Speaker prefixes (`macb`, `macd`, `banq`, `ham`, `bru`) are hapaxes or
near-hapaxes. They will beat thematic words on any unigram ranking of
these files.

## 6. No stoplist, but 221 zeros

Terms with `df = 18` have `idf = 0`. That is an implicit stoplist of
whatever this particular shelf shares — including a few words you might
not call stops (`angry`, `bed`, `children`, `dare`). Add a nineteenth
book that never says `angry` and those weights come back.

## 7. The product script depends on `Text::CSV_XS`

It is only used as a TSV parser. A missing CPAN module is the usual reason
the second script dies; the first script is core Perl. The desk does not
need it.

## 8. `.DS_Store` in `output/tf/`

The original commit shipped Finder metadata next to the TSVs. The product
script skips it (`/^\./`). So does `querydesk.tables.list_table_files`.
