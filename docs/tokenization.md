# Tokenization

tf-idf is only as meaningful as the tokens you feed it. This collection
uses a deliberately crude tokenizer so the Perl original and the Python
rewrite can stay in agreement.

## Rules (both implementations)

For each input line:

1. Strip the trailing newline (`chomp` in Perl).
2. Collapse horizontal and vertical whitespace to a single space.
3. Lowercase A–Z.
4. Delete every character that is not `[a-z0-9]` or whitespace.
   Punctuation, apostrophes, and hyphens disappear.
5. Split on one or more spaces.
6. Drop empty strings.

Examples:

| raw span | tokens |
| --- | --- |
| `Alice's` | `alices` |
| `Oh dear!` | `oh`, `dear` |
| `rabbit-hole` | `rabbithole` |
| `1865` | `1865` |
| `"Hello?"` | `hello` |
| `CHAPTER I.` | `chapter`, `i` |

There is no stemming, no lemmatization, no stoplist, and no sentence
splitting. `alice` and `alices` are different terms. `I` and `i` are the
same term after lowercasing.

## Why this is rough on English

- **Possessives merge.** `Alice's` → `alices`, which is why that token
  ranks in the Alice book.
- **Hyphenation merges.** `waistcoat-pocket` → `waistcoatpocket`.
- **OCR / numbering survives.** The Bible file contributes tokens such as
  `1001` because verse-like numbers are digits, and digits are kept.
- **Function words stay.** `the` is a token. idf, not a stoplist, is what
  drives its score to zero when it appears in every file.

That roughness is a feature of a *toy* pipeline: you can see the effect of
each rule in the top-term lists instead of hiding it behind spaCy.

## Perl detail: `tr/[A-Z]/[a-z]/`

The original script lowercases with

```perl
$txt =~ tr/[A-Z]/[a-z]/;
```

In Perl, `tr///` is a character-by-character transliteration, not a regex
character class. The `[` and `]` are therefore literals. They happen to
map `[` → `[` and `]` → `]`, while `A–Z` map to `a–z`, so case folding
still works. The Python tokenizer just calls `str.lower()`.

## Perl detail: empty tokens and `word_count`

In `tf-idf-values.pl` the length used for tf is:

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

`word_count` increments **before** the empty-string check. Combined with
Perl’s `split(/ +/, ...)`, a leading space on a line produces an empty
field that inflates \(|d|\) without adding a term.

The Python default (`tfidf_toy.tokenize`) does **not** count empty
fields. For an 18-book novel collection the relative tf-idf ranking is
almost unchanged; a few low-order digits in `output/tf/` can differ if you
recompute. Pass `--match-perl-length` if you want the historical
denominator.

## Encoding

Most files in `gutenberg/` are ASCII. `shakespeare-caesar.txt` is
ISO-8859 (latin-1). The Python loader tries UTF-8 and falls back to
latin-1 so a Caesar non-ASCII byte does not crash a recompute.

## What we are not tokenizing on purpose

Project Gutenberg header/footer boilerplate is left in. For a serious
corpus study you would strip `*** START OF THE PROJECT GUTENBERG EBOOK`
banners. Here the headers are short relative to the books, and keeping
them means the checked-in `gutenberg/` files stay untouched replicas of
the original toy dump.
