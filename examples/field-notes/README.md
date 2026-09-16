# Field notes (tiny corpus)

Four short personal notes, each with a different workshop vocabulary.
They exist so the query desk can be checked by hand before you point it
at two million Gutenberg tokens.

| File | Theme | Distinctive terms |
| --- | --- | --- |
| `texts/glacier-cairn.txt` | Alpine hut book | `cairn`, `moraine`, `icefall`, `glacier` |
| `texts/letterpress-proof.txt` | Print shop | `chase`, `quoins`, `tympan`, `furniture` |
| `texts/tide-gauge.txt` | Harbour gauge | `tide`, `stilling`, `datum`, `slack` |
| `texts/herbarium-press.txt` | Plant press | `voucher`, `blotters`, `silica`, `genus` |

Shared glue (`the`, `a`, and a few verbs) is there on purpose so you can
watch IDF drop when a word is not unique.

## Expected tables

`expected/` is the classic `ln(N/df)` product with **`N = 4`**, same
tokenizer as the 2012 Perl. Rebuild:

```bash
python3 -m querydesk field-notes --write-expected
```

## Try

```bash
python3 -m querydesk field-notes
python3 -m querydesk field-notes --query "cairn moraine icefall"
python3 -m querydesk field-notes --query "chase quoins tympan"
python3 -m querydesk field-notes --query "stilling datum slack"
python3 -m querydesk field-notes --query "voucher blotters silica"
```

Full fractions: [docs/05-field-notes-walkthrough.md](../../docs/05-field-notes-walkthrough.md).
