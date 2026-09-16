# Personal commonplace book

Twelve short notes written for this study kit. They are not Gutenberg texts
and they are not workplace writing. Each one is seeded with a tight
vocabulary so classic TF-IDF can pick the note out of the pile.

| File | About | Terms that should win a query |
| --- | --- | --- |
| `01-darkroom.txt` | Wet printing | enlarger, hypo, fixer, dodge, Dektol |
| `02-tide-pool.txt` | Minus tide | anemone, limpet, holdfast, urchin, kelp |
| `03-night-bus.txt` | Last run | terminus, transfer, fluorescent, validator |
| `04-endgame-study.txt` | Rook endings | Lucena, Philidor, zugzwang, opposition |
| `05-fountain-pen.txt` | Nib tuning | tines, feed, converter, baby-bottom |
| `06-winter-swim.txt` | Cold water | afterdrop, neoprene, jetty, cold shock |
| `07-pottery-wheel.txt` | Throwing | centering, grog, leather-hard, bat, cone |
| `08-espresso-dial.txt` | Home espresso | puck, channeling, WDT, blonding, portafilter |
| `09-star-chart.txt` | Backyard sky | averted, Messier, declination, collimation |
| `10-typewriter-ribbon.txt` | Portable typewriter | platen, escapement, pica, typebar |
| `11-beekeeping.txt` | Hive check | queenright, varroa, brood, smoker, super |
| `12-orienteering.txt` | Forest nav | attack point, control flag, reentrant, pace |

```bash
python3 -m shelf_units commonplace
python3 -m shelf_units commonplace "hypo fixer enlarger"
python3 -m shelf_units rank "zugzwang lucena" --units commonplace
```
