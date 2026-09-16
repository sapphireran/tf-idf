# Expected results (check a program against these)

Values use Python `math.log` (natural log) and 12 decimal places. A correct implementation should match to at least 9 decimals. `tfidf_toy.py` writes the same numbers under [`output/`](output/).

\(N=4\). Each document length is 9.

## IDF

| token | df | idf |
| --- | ---: | ---: |
| `and` | 4 | 0 |
| `baker` | 2 | 0.693147180560 |
| `bread` | 2 | 0.693147180560 |
| `climbed` | 1 | 1.386294361120 |
| `cracked` | 1 | 1.386294361120 |
| `followed` | 2 | 0.693147180560 |
| `heated` | 1 | 1.386294361120 |
| `hiker` | 1 | 1.386294361120 |
| `oven` | 1 | 1.386294361120 |
| `rose` | 2 | 0.693147180560 |
| `scored` | 1 | 1.386294361120 |
| `singer` | 1 | 1.386294361120 |
| `song` | 1 | 1.386294361120 |
| `the` | 4 | 0 |
| `trail` | 1 | 1.386294361120 |

## tf × idf (ranked)

### `01-bakery-morning.txt`

| token | tf×idf |
| --- | ---: |
| `bread` | 0.154032706791 |
| `cracked` | 0.154032706791 |
| `scored` | 0.154032706791 |
| `baker` | 0.077016353396 |
| `and` | 0 |
| `the` | 0 |

### `02-ridge-trail.txt`

| token | tf×idf |
| --- | ---: |
| `trail` | 0.308065413582 |
| `climbed` | 0.154032706791 |
| `hiker` | 0.154032706791 |
| `followed` | 0.077016353396 |
| `and` | 0 |
| `the` | 0 |

### `03-bakery-afternoon.txt`

| token | tf×idf |
| --- | ---: |
| `heated` | 0.154032706791 |
| `oven` | 0.154032706791 |
| `baker` | 0.077016353396 |
| `bread` | 0.077016353396 |
| `rose` | 0.077016353396 |
| `and` | 0 |
| `the` | 0 |

### `04-rehearsal-room.txt`

| token | tf×idf |
| --- | ---: |
| `song` | 0.308065413582 |
| `singer` | 0.154032706791 |
| `followed` | 0.077016353396 |
| `rose` | 0.077016353396 |
| `and` | 0 |
| `the` | 0 |

## Cosine

| pair | cosine |
| --- | ---: |
| `01-bakery-morning.txt` × `03-bakery-afternoon.txt` | 0.250872603002 |
| `03-bakery-afternoon.txt` × `04-rehearsal-room.txt` | 0.064282434653 |
| `02-ridge-trail.txt` × `04-rehearsal-room.txt` | 0.042640143271 |
| all other pairs | 0 |

Highest pair must be the two bakery notes. Three pairs must be exactly 0.
