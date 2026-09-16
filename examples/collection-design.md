# Collection design is the model

idf is not a property of a word. It is a property of a word **in a collection**. The four-line toy corpus makes that mechanical; the Gutenberg pocket corpus makes it obvious.

Run the demonstration:

```bash
python3 examples/add_a_document.py
```

## The cats.txt tie, before a fifth document

With \(N = 4\):

\[
\mathrm{tfidf}(\texttt{cat}, \texttt{cats.txt})
  = 0.2 \times \ln 2
  = 0.1 \times \ln 4
  = \mathrm{tfidf}(\texttt{fish}, \texttt{cats.txt})
\]

Frequency and rarity cancel. That is the worked example in [`worked-example.md`](worked-example.md).

## Add one more cat story

`toy-corpus/extra/more-cats.txt` is not part of the default four-file run (the extra directory is skipped by `load_corpus`). Its text is:

```text
the cat ate the fish the kitten likes cream
```

Now \(N = 5\), `cat` appears in three files, `fish` in two:

| term | df before | idf before | df after | idf after |
| --- | --- | --- | --- | --- |
| cat | 2 | ln(4/2) ≈ 0.693 | 3 | ln(5/3) ≈ 0.511 |
| fish | 1 | ln(4/1) ≈ 1.386 | 2 | ln(5/2) ≈ 0.916 |
| kitten, cream, ate | — | — | 1 | ln(5) ≈ 1.609 |

Inside `cats.txt` the tf values did not change. Only idf moved:

| term | tf | tf-idf after |
| --- | --- | --- |
| cat | 0.2 | 0.2 × 0.511 ≈ **0.102** |
| fish | 0.1 | 0.1 × 0.916 ≈ **0.092** |

The tie breaks. `cat` leads because it is still more frequent in that file, and `fish` is no longer a hapax in the collection.

`more-cats.txt` itself will rank `kitten` / `cream` / `ate` above `cat`: those tokens are unique to the new file. That is the same speech-prefix effect as `macb` in the Gutenberg *Macbeth* table, just with kittens.

## Gutenberg is the same phenomenon at 18 documents

- `whale` is only a moderately good identifier because six files mention whales. Add a shelf of sea stories and it would fall further; drop the KJV and Hamlet and it would rise.
- `haue` looks distinctive because only three old-spelling plays are in the mix. A modernized Complete Works would merge it into `have` and bury it.
- `alice` leaks into *Thursday* and *The Parent’s Assistant* as a given name. Those two extra documents are why its idf is ln 6 rather than ln 18.

Changing \(N\) without changing df is not a constant shift. The extra piece is \(\mathrm{tf}(t)\cdot\Delta\ln N\), which boosts high-frequency terms more than rare ones. Rankings inside a file can flip for that reason alone — see [../docs/known-quirks.md](../docs/known-quirks.md).

## Practical rule for this toy

If you want a ranking you can defend, write down the file list. The 18 names in [../docs/corpus.md](../docs/corpus.md) *are* the model. The helpers never pretend otherwise.
