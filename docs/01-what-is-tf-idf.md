# What tf-idf is measuring

Term frequency–inverse document frequency is a ranking heuristic, not a
language model. It answers a narrow question:

> In this one document, which words are both *used* and *unusual
> enough in the rest of the collection* to be worth noticing?

That is why `alice` rises to the top of `carroll-alice.txt` and `whale`
rises to the top of `melville-moby_dick.txt` in the committed
`output/tfidf/` tables. Those words are common *inside* their books
and rare *across* the eighteen-book sample.

## Two pressures, one product

The score is a product of two pressures that pull in opposite
directions.

**Term frequency (TF)** asks how concentrated a word is in the document
you care about. If *gryphon* appears often in *Alice* and almost
nowhere else, TF is high for that book.

**Inverse document frequency (IDF)** asks how widely the word is
spread across the collection. Words that appear in every book
(`the`, `and`, `a`) get an IDF of zero in this repository, because
`ln(N / N) = 0`. Words that appear in one book get the largest IDF.

Multiply them and stop words collapse. Character names, invented
creatures, and topical nouns remain.

## What it is not

- It is not a measure of literary quality.
- It does not know that `ham` in the Hamlet table is a speech prefix
  for Hamlet, not a food.
- It does not stem `whale` and `whales` together unless you add that
  step yourself.
- It does not care about word order. After tokenization, each document
  is a bag of counts.

Those limits are useful. They keep the toy example small enough to
recompute and explain. The later pages show exactly which choices this
repo made, then the `examples/` tree gives you a five-document corpus
where the same choices are easy to inspect by hand.

## Why a personal collection is the right size

A web-scale index hides the arithmetic behind ranking layers. Eighteen
books (or five short original essays) keep every statistic visible:

- you can list the documents that contain a term
- you can compute `df` by counting those documents
- you can see IDF fall as a word spreads
- you can rank one book without a search engine

The Gutenberg sample is the historical toy. The tiny corpus in
`examples/tiny_corpus/docs/` is the one you can reread in a minute and
still watch the same math work.
