# Query desk examples

Personal questions to ask the Gutenberg shelf with the same tokenizer
and `ln(N/df)` weights as the 2012 gold tables.

```bash
python3 -m querydesk rank "QUERY"
python3 -m querydesk explain "QUERY"
python3 -m querydesk compare "QUERY" --variants classic,smooth,bm25
```

## Shelf questions

| Query | What you are checking |
| --- | --- |
| `white whale pequod ahab` | Melville should lead; attribution on names + `whale` |
| `gryphon dormouse hatter` | Carroll, even though `alice` is not in the query |
| `knightley hartfield woodhouse` | *Emma*, not the other Austens |
| `thel lyca vales` | Blake’s short file can still win |
| `thane heath witches banquo` | Macbeth; watch folio/speaker tags in `explain` |
| `leaves grass myself` | Whitman — `myself` is weak IDF; `leaves`/`grass` do the work |
| `paradise lost satan` | Milton |
| `father brown` | Chesterton Brown vs Ball vs Thursday |
| `anne elliot kellynch` | *Persuasion* |
| `buster brown` | Burgess, not Chesterton |

## Misses worth running

| Query | Why it is interesting |
| --- | --- |
| `alice` | Three-document IDF; Carroll still wins on TF |
| `the and of` | Universal terms → zero classic IDF → a flat ranking |
| `whale` | Not a hapax (`df = 6`); cosine still prefers Melville |
| `macb macbeth` | Speaker tag versus the name, same file |

Copy-paste list: [sample-queries.md](sample-queries.md).
