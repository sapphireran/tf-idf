# Sample runs

Captured stdout from the commands in [../README.md](../README.md). Regenerated whenever the toy corpus or helpers change.

| File | Command |
| --- | --- |
| `toy-tfidf.stdout.txt` | `perl examples/toy-tfidf.pl --top 6` |
| `toy-lookup.stdout.txt` | `lookup-term.pl` on `cat`, `the`, and `wind` against `examples/toy-output/` |
| `gutenberg-top-terms.stdout.txt` | `top-terms.pl --n 8` on Alice, *Moby-Dick*, and *Emma* |

The tables behind the toy transcript live in `examples/toy-output/` (same shape as `output/`). Rebuild them with `perl examples/toy-tfidf.pl`.
