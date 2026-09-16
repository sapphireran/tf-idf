# 11 — Further reading

Public sources I actually want next to this lab. No workplace
wikis, no internal RFCs, no vendor pitch decks.

## Classical IR

- Karen Spärck Jones, "A statistical interpretation of term
  specificity and its application in retrieval," *Journal of
  Documentation*, 1972. The IDF paper people mean when they say
  "Spärck Jones."
- Gerard Salton and Christopher Buckley, "Term-weighting approaches
  in automatic text retrieval," *Information Processing & Management*,
  1988. SMART-style TF-IDF variants in one place.
- Christopher D. Manning, Prabhakar Raghavan, and Hinrich Schütze,
  *Introduction to Information Retrieval*, Cambridge University Press,
  2008. Especially the chapters on the vector space model and
  evaluation. The book is publicly available from the authors' site.
- Stephen Robertson and Hugo Zaragoza, "The Probabilistic Relevance
  Framework: BM25 and Beyond," *Foundations and Trends in Information
  Retrieval*, 2009. Why TF-IDF grew a length-normalization story.

## Tokenization and English literary text

- The Project Gutenberg license and file-format notes — useful for
  remembering that heading lines and transcriber markup are in-band.
- Any short description of Early Modern English spelling if I start
  taking Shakespeare TF-IDF too literally (`macbeth` vs `macb`).

## This repository's ancestor

- The 2012 blog companion that the first commit points at:
  `http://nlp-stuff.blogspot.com/2012/09/tfidf-example-and-implementation-details.html`
  (the URL is recorded in `git show a170430`; I am not treating a
  possibly-dead blog as a stable citation).
- The Perl scripts in the repository root, read as a specimen in
  [03](03-original-perl-walkthrough.md).

## What I am not citing

Embedding model cards, commercial search APIs, and anything that would
turn this notebook into a survey of current industry stacks. The next
personal experiment after BM25 is still "read a chapter of Manning et
al. and recompute one table," not "call a hosted reranker."
