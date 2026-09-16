# Personal notes

These pages are a reading path for the 2012 Gutenberg TF-IDF toy in this
checkout. They describe **the weights that are already on disk**, not a new
IR system.

| Note | Use it for |
| --- | --- |
| [01 — Weights this repo uses](01-weights-this-repo-uses.md) | `tf`, `idf = ln(N/df)`, the product, and why zeros appear |
| [02 — Perl pipeline](02-perl-pipeline.md) | `tf-idf-values.pl` and `tf*idf-product.pl` |
| [03 — Gutenberg shelf](03-gutenberg-shelf.md) | Eighteen public-domain files, token mass, what ranks high |
| [04 — Query desk](04-query-desk.md) | Asking a question of the shelf and attributing the score |
| [05 — Field notes walkthrough](05-field-notes-walkthrough.md) | Four short documents you can finish by hand |
| [06 — Quirks](06-quirks.md) | `$#files`, empty split fields, folio spellings, `.DS_Store` |
| [07 — Exercises](07-exercises.md) | Practice without looking at the answers |
| [08 — Answers](08-answers.md) | Worked solutions |

Runnable companions live under `examples/` and `querydesk/`. Start with:

```bash
python3 -m querydesk field-notes --query "cairn moraine"
python3 -m querydesk rank "white whale"
```
