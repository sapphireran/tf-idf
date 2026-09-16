# Tokenization

Both Perl scripts and the Python reference treat a token as a run of
letters or digits after a small cleanup. There is no stop-word list,
no stemmer, and no sentence splitter.

## The cleanup, in order

1. Read the file as raw text.
2. Strip the end-of-line character from each physical line.
3. Collapse horizontal and vertical whitespace to a single space.
4. Lowercase ASCII letters.
5. Delete every character that is not a letter, a digit, or
   whitespace. Apostrophes disappear, so `Alice's` becomes `alices`.
6. Split on one or more spaces.

The Python helper `examples/python/tfidf_lab.py:tokenize` follows that
recipe and then drops empty strings. Empty strings appear when a line
is only spaces, or when a cleaned line still has a leading space.
The Perl loop in `tf-idf-values.pl` increments the document length for
those empty pieces and then ignores them as vocabulary keys. On the
Gutenberg texts the difference is small; on a file of blank lines it
would quietly inflate the denominator of TF.

## Consequences you can see in `output/`

Because punctuation is deleted rather than used as a boundary, several
odd tokens survive:

| Surface text | Token | Why it looks that way |
| --- | --- | --- |
| `Alice's` | `alices` | apostrophe removed |
| `o'er` | `oer` | same |
| `221B` | `221b` | digits stay, letters lowercased |
| `Ham.` as a speech tag | `ham` | period dropped |
| `1` as a chapter or verse number | `1` | digits are legal tokens |

The Hamlet table is the clearest demonstration. Speech prefixes
(`ham`, `hor`, `laer`, `ophe`) outrank most content words because they
are repeated on every line of dialogue and are rare in the novels.

## What is *not* done

- No Unicode normalization beyond whatever the source file already
  contains. The Gutenberg sample is ASCII-heavy.
- No case-folding beyond `A-Z` to `a-z`.
- No stop-word removal. IDF is the only thing that suppresses `the`.
- No n-grams. `white rabbit` is two independent terms.
- No document-length cutoff. Title pages, tables of contents, and
  license headers are scored like the rest of the book.

If you want a cleaner experiment, start with
`examples/tiny_corpus/docs/`. Those five files were written for this
lab and do not carry Project Gutenberg boilerplate.
