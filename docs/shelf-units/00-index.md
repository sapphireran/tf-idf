# Shelf units: a personal reading path

The 2012 scripts in the repository root treat each Gutenberg file as one
document. That is the whole method and, it turns out, the whole limitation.
This folder is a personal study kit for the next question: **what if the
document boundary moves?**

Read in this order.

| Note | What it is for |
| --- | --- |
| [01-why-units-matter.md](01-why-units-matter.md) | Why `N` and `df` secretly encode your filing system |
| [02-reconstructing-the-2012-blog.md](02-reconstructing-the-2012-blog.md) | What the original toy still computes, including the `$#files` quirk |
| [03-bible-bookshelf.md](03-bible-bookshelf.md) | One 821k-word file becomes 55 study units |
| [04-chapter-walks.md](04-chapter-walks.md) | Alice, Milton, Moby-Dick, and Austen at chapter scale |
| [05-folio-voices.md](05-folio-voices.md) | Macbeth / Hamlet / Caesar as stacks of speakers |
| [06-commonplace-book.md](06-commonplace-book.md) | Twelve original notes, ranked on purpose |
| [07-passage-windows.md](07-passage-windows.md) | Retrieval when the unit is a sliding window |
| [08-formula-and-quirks.md](08-formula-and-quirks.md) | `tf * ln(N/df)` plus the Perl tokenizer's scars |
| [09-exercises.md](09-exercises.md) | Worked problems against this checkout |
| [10-answers.md](10-answers.md) | Answers, with the commands that produced them |

The code lives in `shelf_units/`. The notes in `examples/commonplace/` are
original. The Gutenberg files are unchanged public-domain text. Nothing here
is workplace writing.

```bash
python3 -m unittest discover -s tests -v
python3 -m shelf_units demo
```
