# Interpreting results

TF-IDF in this project is a **contrast** score, not a measure of literary importance. A high number means "this token is unusually concentrated in this file relative to the other 17." A zero means "this token is everywhere."

## High scores: names, places, and tags

On the committed Gutenberg snapshot, the top of each ranked list is almost always a proper name or a setting word.

| Observation | Example | Why TF-IDF likes it |
| --- | --- | --- |
| Title character | `alice` in *Wonderland*, `emma` in *Emma*, `ahab` in *Moby-Dick* | High TF in one file, low DF |
| Supporting cast | `gryphon`, `dormouse`, `queequeg`, `knightley` | Same pattern, slightly lower TF |
| Place / ship | `pequod`, `nantucket`, `hartfield`, `highbury` | Rare outside that narrative |
| Work-specific myth | `thel`, `lyca` in Blake | Tiny document + unique names |

That is the intended demonstration: the product of "used a lot here" and "almost unused elsewhere."

## Zero scores: the stop-word effect without a stop list

`the`, `and`, `of`, and `a` have IDF `0` in `output/idf.txt` because they occur in all 18 files. Their TF can be the largest value in a TF table (`a` is about `0.024` in *Alice*) and the TF-IDF row is still `0`.

If you add a 19th document that somehow avoids `the`, IDF for `the` becomes `ln(N / 18)` and the word reappears in every ranking. The zero is a property of **this collection**, not of English.

## Length effects

TF is normalized by document length, so a single mention in Blake can outrank several mentions in the King James Bible.

- Blake (~1.4k lines): rare names get TF on the order of `10^-3` to `10^-2`.
- *Moby-Dick* (~23k lines): even `whale` is only about `0.0045` TF-IDF after IDF.
- Bible (~100k lines): only words that are both frequent *and* somewhat Bible-specific (`unto`, `israel`, `saith`) survive at the top.

When you compare two files, compare **rank and membership**, not raw magnitudes.

## Formatting leakage

The three Shakespeare files were not converted to modern prose. Speaker prefixes and Early Modern spelling occupy the top ranks in *Hamlet*:

```text
ham     0.0141    # HAM. → ham
haue    0.0102    # have
hor     0.0068    # HOR.
qu      0.0058    # QUEEN. / QU.
laer    0.0057    # LAER.
```

`hamlet` itself is lower than `ham` because the speaker tag repeats every speech. This is not a bug in the multiplication; it is the tokenizer taking the file literally. If you want character-name rankings for plays, preprocess speaker tags out before running the scripts. [adding-texts.md](adding-texts.md) describes a safe way to keep a cleaned copy beside the original.

## Token-splitting artifacts

Because apostrophes are deleted:

- `Alice's` → `alices` (appears in the *Alice* top list)
- `I'm` → `im`
- `o'er` → `oer` (visible in Blake)

Digits that survive in headers (`1789`, `1865`) become tokens. In a short file they can rank higher than they deserve.

## Author overlap

Austen's three novels share period vocabulary (`mr`, `mrs`). Those tokens have higher DF than `emma` or `harriet`, so they rank below the *Emma*-only cast even though they are frequent. Chesterton's three files do the same for his journalistic diction.

Use `examples/lookup-term.pl` to see DF and IDF when a ranking surprises you:

```bash
perl examples/lookup-term.pl emma mr mrs ahab whale ham hamlet the
```

## Sanity checks

1. **Top terms should be guessable from the title.** If `output/tfidf/carroll-alice.txt` does not put `alice` first, the IDF table is stale or `N` changed.
2. **Collection-wide words should be zero.** `lookup-term.pl the and of` should report IDF `0` on the snapshot.
3. **Toy corpus should match the worked example.** After `perl examples/toy-tfidf.pl`, the ranks in [../examples/worked-example.md](../examples/worked-example.md) should match `examples/toy-output/`.

If a check fails, regenerate only the tree you meant to regenerate. The toy runner never writes to `output/`.
