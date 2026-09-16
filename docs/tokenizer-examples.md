# Tokenizer before / after

Personal crib sheet for the cleanup in `tf-idf-values.pl`. Same rules are
reimplemented in `examples/tiny-corpus/compute_tfidf.py` so the tiny corpus
does not invent a second tokenizer.

Pipeline, per line:

1. Strip the end-of-line character.
2. Collapse runs of whitespace to a single space.
3. Lowercase ASCII letters.
4. Delete every character that is not `[a-zA-Z0-9]` or a space.
   Deletion does **not** insert a space.
5. Split on spaces. Empty fields increment the Perl token counter but are
   not stored as terms.

## Lines from `gutenberg/carroll-alice.txt`

Source, first paragraph after the title:

```
Alice was beginning to get very tired of sitting by her sister on the
bank, and of having nothing to do: once or twice she had peeped into the
book her sister was reading, but it had no pictures or conversations in
it, 'and what is the use of a book,' thought Alice 'without pictures or
conversation?'
```

After the rules, the first sentence is:

```
alice was beginning to get very tired of sitting by her sister on the
bank and of having nothing to do once or twice she had peeped into the
```

Commas, colons, and the newline-between-`the` / `bank` become ordinary
spaces. Nothing exciting yet.

The quoted aside is more interesting:

```
it  and what is the use of a book  thought alice without pictures or
conversation
```

- Leading `'` on `'and` disappears; the token is `and`.
- `'without` becomes `without`.
- `conversation?` becomes `conversation`.
- `Alice` and `alice` are the same term.

## Possessives and hyphenation

| Source span | Stored term(s) | Why |
| --- | --- | --- |
| `Alice's Adventures` (title line) | `alices`, `adventures` | Apostrophe deleted; `s` stays on the name |
| `waistcoat-pocket` | `waistcoatpocket` | Hyphen deleted, no break inserted |
| `TOOK A WATCH` | `took`, `a`, `watch` | Case fold only |
| `1865` in the title header | `1865` | Digits are kept |
| `don't` (if it appeared) | `dont` | Apostrophe deleted |

`alice` and `alices` are different keys in every table. Summing them is a
post-processing choice; the Perl never does it.

## Shakespeare speech prefixes

A typical *Hamlet* cue, conceptually `HAM. To be, or not to be`, becomes
`ham` + `to` + `be` + `or` + `not` + `to` + `be`. `ham` then looks like a
very rare, very frequent content word. That is why it tops
`output/tfidf/shakespeare-hamlet.txt`.

Early Modern spellings are kept as-is after lowercasing: `haue`, `vpon`,
`giue`, `loue`. There is no mapping onto modern `have` / `upon`.

## Bible verse numbers

A verse marker such as `1001` is a legal token. It appears in one document
and gets `idf = ln(18) ≈ 2.890`. `examples/top_terms.py --skip-digits` hides
those rows when you want words instead of apparatus.

## Empty-token example

Take a line that is only punctuation, or that becomes spaces after step 4:

```
---
```

After deletion the line is empty. `split(/ +/, "")` in Perl yields one
empty field. Pass 1 still does `$word_count++`. The TF denominator grows;
no term is stored. A file full of decorative rules would look "longer"
than a human word count.

The tiny-corpus Python script **does not** reproduce that increment. Its
denominator is `len(tokens)` after dropping empties. The Gutenberg
`output/` snapshot still has the Perl behavior.

## Recreating a single line

```bash
python3 - <<'PY'
from pathlib import Path
import sys
sys.path.insert(0, "examples/tiny-corpus")
from compute_tfidf import tokenize
print(tokenize("[Alice's Adventures in Wonderland by Lewis Carroll 1865]"))
print(tokenize("waistcoat-pocket"))
print(tokenize("HAM.  To be, or not to be:"))
PY
```

Expected:

```
['alices', 'adventures', 'in', 'wonderland', 'by', 'lewis', 'carroll', '1865']
['waistcoatpocket']
['ham', 'to', 'be', 'or', 'not', 'to', 'be']
```
