# Mini corpora

Two tiny collections you can score by hand. Both use the same tokenizer
and the same raw TF × unsmoothed IDF product as the Perl scripts. Run
them with:

```bash
python3 examples/mini_tfidf.py examples/mini_corpus/three_docs
python3 examples/mini_tfidf.py examples/mini_corpus/literary_snippets
```

Add `--variant smooth` or `--variant log_tf` to see the alternatives
described in [../../docs/quirks-and-variants.md](../../docs/quirks-and-variants.md).

## `three_docs/`

Designed so every number in [../../docs/tf-idf-math.md](../../docs/tf-idf-math.md)
can be checked with a calculator.

| File | Tokens |
| --- | --- |
| `the_harbor.txt` | the, whale, swims, in, the, harbor |
| `the_song.txt` | the, whale, sings, a, song |
| `the_bird.txt` | the, bird, sings, a, song |

\(N = 3\). `the` is in every document, so its IDF is 0. `bird`, `swims`,
`in`, and `harbor` appear once in the collection, so they share
\(\ln 3\). `whale` is the term that ties the first two documents
together.

Expected ranking (raw variant):

- harbor document: `swims` / `in` / `harbor` (tie), then `whale`, then `the`
- song document: `whale` / `sings` / `a` / `song` (tie), then `the`
- bird document: `bird` first, then the three shared content words, then `the`

`tests/test_mini_tfidf.py` asserts the exact products.

## `literary_snippets/`

Three two-line pastiches, still small enough to print in full, closer
to the Gutenberg filenames.

| File | About |
| --- | --- |
| `alice.txt` | Carroll opening + the rabbit |
| `ishmael.txt` | Melville opening + a whale |
| `hamlet.txt` | The soliloquy's first two lines |

This one is for qualitative checks: `alice` and `rabbit` should rise in
the first file, `ishmael` / `whale` in the second, `nobler` / `suffer`
in the third. `the` should still be zero if it appears in all three
snippets (it does). `to` appears twice in Hamlet's first line and in no
other snippet, so it will look "distinctive" — a useful reminder that
TF-IDF is not a literary critic.

Full token tables are printed by `mini_tfidf.py`; there is no separate
gold file beyond the three-docs unit tests.
