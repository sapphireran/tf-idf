# Examples

| Path | What it is |
| --- | --- |
| [field-notes/](field-notes/) | Four workshop notes + expected `ln(N/df)` tables, `N = 4` |
| [query-desk/](query-desk/) | Questions to rank against the Gutenberg gold tables |

```bash
make field-notes
make alice
python3 -m querydesk rank "white whale pequod ahab"
```
