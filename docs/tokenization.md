# Tokenization

`tf-idf-values.pl` cleans each line of each Gutenberg file before it counts anything. The Python example copies the same rules so the tiny corpus and a Gutenberg rerun stay comparable.

## Steps, in order

For every line of input:

1. **Drop the newline.** `chomp`.
2. **Collapse horizontal and vertical whitespace** to a single space: `$txt =~ s/[\h\v]+/ /g`.
   Tabs, spaces, and the unusual whitespace that shows up in some Gutenberg prose become one separator.
3. **Lowercase ASCII letters.** `$txt =~ tr/[A-Z]/[a-z]/`.
   In Perl this `tr///` range also lists the bracket characters, but `[` maps to `[` and `]` maps to `]`, so the effect on letters is ordinary A–Z → a–z.
4. **Delete everything that is not alphanumeric or whitespace:** `$txt =~ s/[^a-zA-Z\d\s]//g`.
   Punctuation, apostrophes, quotes, underscores, and em-dashes disappear. Digits stay.
5. **Split on one or more spaces:** `split(/ +/, $txt)`.
6. **Skip empty strings.** A line that was only punctuation becomes no tokens.

The same line is never joined with the next line before splitting. A hyphenated word broken across a Gutenberg line break becomes two tokens (`wonder` / `land` rather than `wonderland`) if the hyphen is stripped and a newline already split the letters.

## What this does to real words

| original text | tokens |
| --- | --- |
| `Alice's Adventures` | `alices`, `adventures` |
| `I'm late!` | `im`, `late` |
| `Oh dear!` | `oh`, `dear` |
| `the Mock Turtle` | `the`, `mock`, `turtle` |
| `1865` | `1865` |
| `don't` | `dont` |
| `self-same` | `selfsame` if on one line; `self` `same` if hyphenated at a break after stripping |

There is **no** stopword list. Function words are counted and later zeroed by IDF when they occur in every document.

There is **no** stemmer. `whale` and `whales` are different terms. That is why both appear near the top of Moby-Dick's TF-IDF list.

There is **no** case-sensitive proper-name pass. `Alice` and `alice` are the same term, which is what you want for this experiment.

## Digits and Gutenberg leftovers

Project Gutenberg files include:

- years and chapter numbers (`1865`, `1`, `10`)
- leftover catalog numbers (the `00021053` style strings in Milton)
- stage directions and speaker prefixes in the Shakespeare files (`HAM.`, `MACB.`)

After cleaning, those become ordinary terms. A catalog number that occurs in one file gets the maximum IDF (`ln(18/1)`) and can look "important" if you sort blindly. They are rare enough that they usually lose to character names once you look at the head of the list, but they occupy space in `idf.txt` (57,368 terms).

## Speaker tags in the plays

The Shakespeare texts keep abbreviated speech prefixes. After tokenization:

| book | tag that ranks at the top |
| --- | --- |
| Hamlet | `ham` |
| Macbeth | `macb` |
| Julius Caesar | `bru` |

Those are **not** vocabulary about Denmark, Scotland, or Rome. They are "who is speaking" labels that happen to be unique to one file. When you read [interpreting-results.md](interpreting-results.md), treat the first one or two play terms as formatting, then look at `horatio`, `banquo`, `cassius`.

The Python top-term reader does not strip them. Filtering speaker tags is left as an exercise; the cleanest fix is to preprocess the plays.

## Unicode and non-ASCII

The Perl script operates on bytes / ASCII classes (`A-Z`, `\d`). Most of this Gutenberg snapshot is ASCII. If a future file includes curly quotes or accented characters, step 4 will strip those bytes or characters depending on Perl's locale, and you may get broken tokens. The teaching corpus does not rely on that path.

## Matching the rules in another language

A Python sketch that stays close to the Perl:

```python
import re

def tokenize_line(line: str) -> list[str]:
    line = line.replace("\n", "").replace("\r", "")
    line = re.sub(r"[\h\v]+", " ", line, flags=re.UNICODE)
    # [\h\v] needs a fallback on older Python; spaces/tabs/newlines are enough here:
    line = re.sub(r"\s+", " ", line)
    line = line.lower()
    line = re.sub(r"[^a-zA-Z0-9\s]", "", line)
    return [tok for tok in line.split(" ") if tok]
```

`examples/python/tfidf_example.py` uses that logic on whole files (join lines with a space after the same per-line clean, equivalent for these texts because newlines already become separators).

## Why not a nicer tokenizer?

This project is documenting a small Perl experiment, not proposing a standard. A "nicer" tokenizer (Unicode word breaks, keeping inner apostrophes, splitting speaker tags) would change every committed number in `output/`. The notes keep the historical rules so the tables stay explainable.

If you want a second, cleaner pass, add it as a new script and write a new output directory. Do not silently replace `output/tfidf/` or the tiny-corpus `expected/` files.
