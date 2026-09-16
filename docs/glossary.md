# Glossary

**collection / corpus.** The set of documents being scored together.
IDF is defined on this set, not on the English language.

**cosine similarity.** The cosine of the angle between two TF-IDF
vectors. `1` means the same direction, `0` means no shared weighted
terms.

**df, document frequency.** How many documents contain a term at least
once. Written to `output/df.txt`.

**document.** One file. In the Gutenberg sample, one book or play. In
the tiny corpus, one short original essay.

**idf, inverse document frequency.** `ln(N / df)` in this repo. Large
when a term is rare across documents.

**N.** Number of documents in the collection. 18 for the committed
Gutenberg tables, 5 for the tiny corpus, 3 for the classroom example.

**term / token.** A lowercase run of letters or digits after
punctuation has been deleted.

**tf, term frequency.** `count / document_length` in this repo. A
proportion, not a raw count.

**tf-idf.** The product `tf * idf`. Written to `output/tfidf/` and
`examples/tiny_corpus/expected/tfidf/`.

**variant.** A named formula bundle in the Python reference: `repo`,
`log_tf`, or `smooth_idf`. See [variants](07-algorithm-variants.md).

**vocabulary.** The sorted union of terms across the collection.

**worked example.** The three-sentence collection `cats sit on mats` /
`dogs sit on logs` / `cats chase dogs`, expanded cell by cell in
[the worked example page](08-worked-example.md).
