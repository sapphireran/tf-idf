# Answers

## 1. Recover `N`

\[
e^{2.89037175789616} = 18
\]

or `ln(18) = 2.8903717578961645`. Gold hapax IDF is exactly `ln(18/1)`.

## 2. Alice is not a hapax

\[
\mathrm{idf}(\textit{alice}) = \ln(18/3) = \ln 6 = 1.791759469228055
\]

\[
\mathrm{tfidf} = 0.0144867549668874 \times 1.791759469228055 \approx 0.0259568
\]

which matches `output/tfidf/carroll-alice.txt`.

## 3. Why `macb` beats `macbeth`

Both are hapaxes (`idf ≈ 2.8904`). TF-IDF then reduces to TF. The speaker
prefix is printed on most of Macbeth’s lines, so `count(macb) > count(macbeth)`.
A second, smaller effect: `macbeth` also appears in stage directions and
other speakers’ lines, but still less often than the tag.

## 4. Empty-field denominator

Perl `split(/ +/, " cairn ice")` yields `("", "cairn", "ice")`.
`word_count = 3`, `tf(cairn) = 1/3`, not `1/2`.

## 5. Universal term

`idf(the) = ln(18/18) = 0`, so `tfidf(the, Moby-Dick) = 0`.

## 6. Field-notes ranking

- `cairn icefall` → `glacier-cairn.txt` (`cairn`, `icefall`)
- `tympan quoins` → `letterpress-proof.txt` (`tympan`, `quoins`)
- `silica voucher` → `herbarium-press.txt` (`silica`, `voucher`)

Confirm with `python3 -m querydesk field-notes --query "…"`.

## 7. `$#files` versus gold

`readdir` names: `.`, `..`, `.DS_Store`, 18 texts → 21 entries.
`$#files = 20`. Hapax IDF becomes `ln(20) ≈ 2.9957` instead of `ln(18) ≈ 2.8904`
(about **+3.6%**). Every other IDF row scales by `ln(20/df)/ln(18/df)`, which
is *not* a constant factor.

## 8. Cosine versus dot

`whale` has `df = 6` on this shelf (`idf ≈ 1.0986`), so it is not a hapax.
Dot product is `q_tfidf(whale) * d_tfidf(whale)`. For a one-term query that
is just a scaled `tf(whale, d) * idf(whale)^2`. *Moby-Dick* still wins
because its `tf(whale)` is far larger than anyone else’s — the KJV and
Chesterton mention whales, but not as a dominant unigram. Dot product
*would* misbehave for a query of common medium-IDF words (`sea`, `man`,
`god`) where the Bible’s extra non-zeros pile up. Prefer cosine (the
default) for “which book is this about?”

## 9. Smooth IDF sign

\[
\ln(18/19) < 0
\]

Universal terms get a *negative* weight and start behaving like “this word
is evidence *against* a match.” Classic IDF keeps them at zero, which is
easier to explain next to the gold TSVs.

## 10. Attribution sanity

Contributions are `q_tfidf[t] * d_tfidf[t]`. The query only has `gryphon`
and `dormouse`, so those two rows dominate (`dormouse` is a hapax; `gryphon`
has `df = 2`). `alice` has a huge document weight but **zero query TF**, so
it does not appear. Attribution is not “top terms in the book”; it is “top
terms in the *overlap*.”
