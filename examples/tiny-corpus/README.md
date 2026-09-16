# Tiny corpus

Three original paragraphs (cats, dogs, baking) written for this
repository. They are long enough that TF values are not all `1/N`
and short enough that the top terms are still obvious.

Design choices:

- Cats and dogs share a template ("sunny … chase … nap in the same
  patch of sun … soft fur … fills the … afternoon") so IDF has
  something to down-weight.
- Distinctive nouns are repeated (`purr` / `yarn` vs `bark` / `ball`
  vs `bread` / `dough` / `ovens`) so TF has something to up-weight.
- Baking is a third cluster with almost no lexical overlap, standing
  in for "a document from another domain."

The texts are personal study material, not excerpts from the
Gutenberg dump.
