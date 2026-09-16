# Known quirks

This page is a list of things that surprised me when I reread the scripts next to `output/`. None of them are mysteries once you see the code; all of them change how you should read a ranked list.

## 1. `N` in Perl is not "number of books"

`tf-idf-values.pl` sets

```perl
my $n = $#files;
```

`@files` is `readdir("gutenberg")`, which includes `.` and `..` and, in this snapshot, `.DS_Store`. `$#files` is the last index of that array.

The committed `output/idf.txt` nevertheless matches **`N = 18`**:

```
ln(18 / 1) = 2.89037175789616
```

So the tables in `output/` were produced with one document per `.txt`. A rerun on a macOS checkout that still has `.DS_Store`, or on a listing that includes extra dotfiles, will change every IDF and every TF-IDF.

The Python example counts non-hidden input files and uses that as `N`. That is the definition these notes use everywhere else.

If you want the Perl to match the notes, replace `$#files` with a count of files that actually entered the TF loop.

## 2. Collection-wide words are exactly zero

Because IDF is `ln(N / df)` with no `+ 1`, any term with `df = N` has IDF `0` and TF-IDF `0`. In this collection that includes `the`, `and`, `to`, `a`, `of`, `in`, `i`, `it`, `that`, `not`, `was`, `she`, and many other function words.

That is a feature for teaching. It is a bug if you planned to feed the vectors to cosine similarity and expected stopwords to still contribute a little.

## 3. Speaker prefixes beat plot words in the plays

The Shakespeare files keep `HAM.`, `MACB.`, `BRU.` style labels. After tokenization they become `ham`, `macb`, `bru` — short and very frequent in that play. `macb` and `bru` are unique to one file (`df = 1`). `ham` is not: it also occurs in the Bible, Chesterton, Austen, and Edgeworth (the food / name), so `df = 5`. It still leads Hamlet because the speech prefix is used hundreds of times.

| file | top term | df | what it actually is |
| --- | --- | --- | --- |
| `shakespeare-hamlet.txt` | `ham` | 5 | speech prefix for Hamlet (plus other "ham") |
| `shakespeare-macbeth.txt` | `macb` | 1 | speech prefix for Macbeth |
| `shakespeare-caesar.txt` | `bru` | 1 | speech prefix for Brutus |

Read the next ten terms. `horatio`, `banquo`, `cassius` are the vocabulary you probably wanted.

## 4. Early Modern spelling is "rare" in a mixed collection

`haue`, `vpon`, `selfe`, `giue`, `ile`, `vs` rank high in every play and in Milton because the Austen / Carroll / Burgess files use modern `have`, `upon`, `self`. IDF is doing its job: those spellings are rare *here*. They are not rare in 1600s English.

If you built a collection of only First Folio plays, those forms would sink.

## 5. Apostrophes are deleted, not treated as letters

`Alice's` → `alices`. `I'm` → `im`. `don't` → `dont`. You will see `alices`, `im`, and `didnt` in the ranked lists. They are not OCR errors.

## 6. No stemming, so plurals are separate terms

`whale` and `whales` both appear in the Moby-Dick head. So do `boat` / `boats` and `anarchist` / `anarchists`. A stemmer would merge them; this pipeline will not.

## 7. Names are not exclusive to "their" book

A high TF-IDF score does not mean `df = 1`. From the committed DF table:

| term | df | also appears in |
| --- | --- | --- |
| `alice` | 3 | *Thursday*, *The Parent's Assistant* |
| `gryphon` | 2 | *Paradise Lost* |
| `hatter` | 3 | Chesterton *Brown*, Whitman |
| `emma` | 2 | *Persuasion* |
| `ahab` | 2 | King James Bible (the original Ahab) |
| `whale` | 6 | Bible, Whitman, Bryant, Hamlet, *Ball and the Cross* |
| `hamlet` (the word) | 6 | Moby-Dick, Whitman, Chesterton, Austen, Edgeworth |

TF-IDF still puts `alice` first in Carroll because TF is large. `ahab` in Moby-Dick is the captain; `ahab` in the KJV is a different person who contributes to DF.

## 8. Digits and catalog leftovers are first-class terms

`1865`, `00`, `00021053`, chapter numbers, and Gutenberg residue all have rows in `idf.txt`. A hapax catalog number gets the maximum IDF. They rarely win a book's ranking because their TF is tiny, but they inflate the vocabulary to 57k terms.

## 9. `tf*idf-product.pl` must be quoted

The filename contains `*`. Unquoted `perl tf*idf-product.pl` is a glob. Quote it or call `perl ./tf\*idf-product.pl`.

## 10. `df-sorted.txt` is not part of the current pipeline

The file exists and is huge. Neither Perl script writes it. Do not use it as a source of truth; sort `df.txt` yourself.

## 11. Hash iteration order leaks into `df.txt`

The list of filenames on each DF row is `keys %{ $df{$t} }`. That order is not a documented sort. Numeric DF is reliable; the name list is a set written as a string.

## 12. `use strict` without `use warnings`

The scripts will not tell you about uninitialized IDF lookups. After a consistent two-script run this is fine. If you hand-edit `idf.txt` and leave a term out, script 2 will treat the missing IDF as `0` and keep going.

## 13. One document = one file, including the whole KJV

The King James file is 821k tokens. It is a single document for DF purposes. A word that appears once in Genesis and once in Revelation still has `df += 1`, not 2. If you split the Bible by book, every biblical name's IDF would drop.

## 14. Line-broken hyphenation splits words

Gutenberg line width is ~70 characters. A hyphen at a line break is stripped, and the newline is already a split, so `wonder-` + `land` can become `wonder` and `land`. Some "mystery" tokens are just wrap artifacts.
