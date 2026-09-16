# 05 — IDF smoothing variants

"IDF" in conversation usually means \(\log(N / n_t)\). Implementations
almost never ship that formula unmodified, because it misbehaves at
the edges.

The lab names four flavors. All of them take natural logs. All of
them are computed on the same tokenized shelf so the only moving
part is the rarity function.

## `classic`

\[
\mathrm{idf}_{\mathrm{classic}}(t) = \log \frac{N}{n_t}
\]

- Hapax: \(\log N\).
- Collection-wide term: \(0\).
- Undefined if \(n_t = 0\) (a query term never seen). The lab returns
  `0.0` and records a miss rather than raising.

This is the 2012 table, with \(N = 18\) on Gutenberg.

## `smooth` (plus-one)

\[
\mathrm{idf}_{\mathrm{smooth}}(t) = \log \frac{N + 1}{n_t + 1}
\]

Every count is shifted by one document of imagination. Collection-wide
terms still get a tiny positive weight
\(\log((N+1)/(N+1)) = 0\) — wait. That is still zero when \(n_t = N\).

The more common plus-one that *keeps* a residual on common terms is

\[
\log \frac{N + 1}{n_t + 1} + 1
\]

or

\[
\log \frac{N}{n_t} + 1
\]

I implement the second family as `smooth`:

\[
\mathrm{idf}_{\mathrm{smooth}}(t) = \log \frac{N + 1}{n_t + 1} + 1
\]

so a term in every document still contributes `1` rather than
vanishing. That is the point of the experiment: does `the` deserve
a floor?

## `probabilistic`

\[
\mathrm{idf}_{\mathrm{prob}}(t) = \log \frac{N - n_t}{n_t}
\]

This is negative when \(n_t > N/2\). Negative IDF is not a bug in
the formula; it is a statement that a majority-shelf word should
*hurt* a document that uses it. Cosine on mixed-sign vectors is
legal but easy to misread. I keep this flavor so I can see the sign
flip on `the` versus `whale`.

When \(n_t = N\), the numerator is 0 and the log is \(-\infty\). The
lab clamps to a large negative sentinel only in display; the scorer
treats it as `0.0` so rankings do not explode. That clamp is a
notebook choice, not a theorem.

## `bm25`

Robertson–Sparck Jones IDF can go negative when \(n_t\) is large.
The lab uses the Lucene-style rewrite that stays positive:

\[
\mathrm{idf}_{\mathrm{bm25}}(t) = \log\left(1 + \frac{N - n_t + 0.5}{n_t + 0.5}\right)
\]

Paired with the usual TF saturation (see `tfidf/weights.py`):

\[
\mathrm{tf}_{\mathrm{bm25}}(t,d) =
\frac{f_{t,d}\,(k_1+1)}{f_{t,d} + k_1\bigl(1-b+b\,|d|/\mathrm{avgdl}\bigr)}
\]

Defaults: \(k_1 = 1.2\), \(b = 0.75\). I am not tuning them. They
exist so a query can be ranked two ways on the same tokens.

## How I compare them

```bash
python3 -m tfidf compare "white whale" --corpus gutenberg
python3 -m tfidf compare "the and of" --corpus tiny
```

What I expect to see:

- `classic` and `bm25` should both put *Moby-Dick* first for
  `white whale`. If they do not, the bug is elsewhere.
- `smooth` should lift stopword-only queries off the floor. That is
  not a virtue. It is a demonstration that a floor reintroduces
  length bias: the longest document wins `the and of`.
- `probabilistic` should look hostile to common words and can
  reorder mid-list documents that differ mainly in function words.

Worked numbers for the tiny corpus live in
[04](04-worked-example-tiny-corpus.md).
