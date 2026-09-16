# Quirks and design choices

This toy is small enough that every awkward decision shows up in the tables. The list below is the map of those decisions. None of them are bugs in a production sense — there is no production — but they change how you should read a ranking.

## 1. `N` is 18 in the tables, `$#files` in the Perl

`tf-idf-values.pl` sets

```perl
my $n = $#files;
```

after `readdir("gutenberg")`. That is the last index of the directory listing, not the number of books. The committed `output/idf.txt` nevertheless matches `ln(18 / df(t))` exactly (57,367 of 57,368 rows; the remaining row is the `thatyou` glitch below).

Commit `b50ebb9` ("Bugfix: correcting idf values in calculating number of files") rewrote the tables and left the script as-is.

**Read the snapshot as `N = 18`.** Re-runs should count processed documents, which is what the Python pipeline does.

## 2. Empty `split` fields inflate the TF denominator

```perl
$word_count++;
if($d ne "") { $tf{$d}++; ... }
```

Perl `split(/ +/, " alice")` yields `("", "alice")`. The empty field is not a token, but it is a count. Any line that still has a leading space after whitespace collapse slightly lowers every `tf` in that book.

The Python tokenizer exposes this as `count_empty_tokens=True` (compat mode) versus `False` (clean mode). The tiny-corpus walkthrough uses clean mode because those three files have no leading spaces.

## 3. Apostrophes vanish, so `Alice's` ≠ `alice`

The normalizer deletes `'` with the rest of the punctuation. Visible effects in Alice:

| Surface form | Token |
| --- | --- |
| `Alice` | `alice` |
| `Alice's` | `alices` |
| `I'm` | `im` |
| `don't` | `dont` |
| `the Gryphon` | `gryphon` |

`alices` ranks in Alice's top ten because it is unique (`df = 1`) and the book uses the possessive often. A lemmatizer would have merged it with `alice` and pushed the name even higher.

## 4. Headers, years, and numbers are tokens

Alice's file begins with a bracketed title line. After tokenization, `1865` is a hapax of the book. The Bible contributes thousands of verse numbers. `idf` treats `1001` the same way it treats `dormouse`: unique string, maximum weight per occurrence.

If you want literary terms only, drop tokens that are purely digits. The ranking tools accept `--drop-digits`.

## 5. Folio spelling and speech prefixes dominate Shakespeare

Macbeth's top weights are not "ambition" or "tomorrow". They are:

| Token | Why it wins |
| --- | --- |
| `macb` | Speech prefix, unique, very frequent |
| `haue` | Folio `have`, shared by the three plays (`df = 3`) |
| `macbeth` | Character name, unique |
| `macd` | Macduff's prefix |
| `vpon` / `vs` | Folio `upon` / `us` |

This is a tokenizer succeeding at its job. It is also a reminder that `tf * idf` ranks **strings**, not characters or themes.

## 6. Zero IDF is the stopword list

221 tokens have `df = 18` and therefore `idf = 0`. The list is not only function words. It includes `house`, `world`, `children`, `death`, `morning`, `water`, `friend`, `secret`, `tongue`.

Those content words are not semantically empty. They are merely useless *as discriminators in this 18-book sample*. A different sample would revive them. That is why a frozen stopword file and a zero-IDF list are not the same thing.

Full zero-IDF list from `output/idf.txt`:

```
a about after against age all alone am among an and angry another any
are as at away back be bed before besides best both breath brought but
by call came can cannot children close come could dare day dead death
did do done doubt each else end eye eyes face faces fall fast for
forgot found free friend from full gently go going gone good great
ground had hand happy has he head heard her here high him his home
house how i if ill in indeed into is it know laugh lay left let life
like little long lost made make making man many may me meet met might
mine more morning most must my next night no noise none nor not
nothing now of off old on once one or our out part past place please
put ready reason red rise round run said same saw say saying secret
see set she should sight sit so some sound speak stand still stood
such take tell that the their them then there these they thing this
those though thought through till time times to told tongue too truth
two want was water way we well went were what when where which while
who whose why will wise wish with within without word world would
write yet you young your
```

## 7. One corrupt `idf` cell

```
thatyou	2.89037175789616y
```

`thatyou` looks like a missing-space join (`that` + `you`) and the value has a trailing `y`. The numeric prefix is the correct unique-token IDF. Readers in `examples/python/` accept the prefix and record the row as dirty.

This is left in place. The snapshot is historical.

## 8. `.DS_Store` files

The original commit included macOS folder metadata under the repo root, `gutenberg/`, and `output/`. Those files are not documents. The Perl skip rule (`/^\./`) ignores them. They are not part of the Python corpus walk either.

## 9. No stemming, no case folding beyond ASCII, no Unicode story

The blog post is explicit: the regexes are not an exhaustive normalizer, and there is no UTF-8-to-ASCII step. For this English ASCII sample that is fine. `café` would keep `caf` after the non-alphanumeric strip if a non-ASCII file were added.

## 10. Cosine is not in the original scripts

The 2014 write-up walks through document vectors and a dot product on a four-word toy. This repository's original code stops at `tf * idf` tables. Similarity lives in the later Python example so the Perl snapshot can stay untouched.
