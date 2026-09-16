# Tiny corpus

Four one-sentence notes, nine tokens each after the same cleanup the Perl scripts use. Small enough to score with a pencil; large enough to show why `the` / `and` vanish and why the two bakery notes sit closer than a bakery note and a song.

| File | Text | About |
| --- | --- | --- |
| [`documents/01-bakery-morning.txt`](documents/01-bakery-morning.txt) | The baker scored the bread and the bread cracked. | bakery |
| [`documents/02-ridge-trail.txt`](documents/02-ridge-trail.txt) | The hiker followed the trail and the trail climbed. | outdoors |
| [`documents/03-bakery-afternoon.txt`](documents/03-bakery-afternoon.txt) | The baker heated the oven and the bread rose. | bakery |
| [`documents/04-rehearsal-room.txt`](documents/04-rehearsal-room.txt) | The singer followed the song and the song rose. | music |

Shared function words: `the`, `and` (in all four → idf 0).

Shared content words:

- `baker`, `bread` — bakery pair
- `followed` — trail + rehearsal
- `rose` — afternoon bakery + rehearsal (verb, two senses; the method does not care)

Unique content words: `scored`, `cracked`, `hiker`, `trail`, `climbed`, `heated`, `oven`, `singer`, `song`.

## Read vs run

- Arithmetic, every intermediate: [`worked-example.md`](worked-example.md)
- Rounded tables to check a program against: [`expected-results.md`](expected-results.md)
- Regenerated files: [`output/`](output/)

```bash
python3 examples/python/tfidf_toy.py examples/tiny-corpus/documents \
    --write-dir examples/tiny-corpus/output
python3 examples/python/rank_terms.py \
    --from-table examples/tiny-corpus/output/tfidf/01-bakery-morning.txt
python3 examples/python/similar_docs.py \
    --table-dir examples/tiny-corpus/output/tfidf
```
