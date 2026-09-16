# Reading-companion examples

Standard-library scripts that read the checked-in `output/tfidf`
tables. They do not rerun the 2012 Perl and they do not write gold
files.

From the repository root:

```bash
python3 examples/reading-companion/run_checks.py
python3 examples/reading-companion/term_atlas.py alice --top 12
python3 examples/reading-companion/cosine_map.py --neighbors
python3 examples/reading-companion/cosine_map.py --group austen
python3 examples/reading-companion/query_shelf.py white whale ahab
python3 examples/reading-companion/folio_spellings.py
python3 examples/reading-companion/length_study.py
python3 examples/reading-companion/boilerplate_scan.py
```

Each script accepts `--check` and exits non-zero if a number quoted
in `docs/reading-companion/` has drifted on this snapshot.

| Script | Job |
| --- | --- |
| `shelf.py` | Loader, cosine, query ranking |
| `term_atlas.py` | Heaviest terms per book |
| `cosine_map.py` | Pairwise map, neighbors, author means |
| `query_shelf.py` | Cookbook queries |
| `folio_spellings.py` | Shared Folio spine + presence test |
| `length_study.py` | Words / vocab / top term / L2 |
| `boilerplate_scan.py` | Raw `gutenberg`/`ebook` counts vs weights |
| `run_checks.py` | All `--check` modes |

`shelf.py` walks upward until it sees `output/tfidf` and
`gutenberg`, so the scripts still work if you invoke them by
absolute path.
