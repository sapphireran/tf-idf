# 10 — Glossary

Short definitions in the sense I use them in this notebook. Not a
textbook.

**BM25.** A family of ranking functions that damp term frequency and
normalize by document length, with an IDF that stays well-behaved when
\(n_t\) is large. I treat it as the usual next formula after TF-IDF,
not as a production default I have tuned.

**Collection / shelf / corpus.** The set of documents IDF is computed
from. Here, either the four tiny texts or the eighteen Gutenberg
files. IDF is meaningless without naming the shelf.

**Cosine similarity.** Dot product of two vectors after each is scaled
to unit Euclidean length. Cancels pure magnitude, so a short poem and
a long novel can still be compared if their *directions* match.

**df, \(n_t\).** Document frequency: how many documents contain term
\(t\) at least once. Presence, not count.

**Hapax (document-level).** A term that appears in exactly one
document on the shelf. IDF is then \(\log N\) (textbook form).

**IDF.** Inverse document frequency. A term's rarity on the shelf.
Several formulas exist; "the" IDF does not exist.

**Inverted index.** A map from term → posting list (documents, and
usually positions or frequencies). The 2012 Perl never builds one; it
writes flat tables. The Python lab keeps a modest in-memory invert
for ranking.

**SMART notation.** Three-letter codes for TF, IDF, and normalization
on the document and query sides (`ltc.lnn`, and so on).

**Stopword.** A token I choose to drop because it is too common to
help. IDF already down-weights collection-wide words; a stoplist is a
blunt extra knife. I keep one small list for experiments and do not
treat it as linguistics.

**tf, \(f_{t,d}\).** Term frequency: how often \(t\) occurs in \(d\).
Raw or normalized, depending on the sentence.

**Token.** What remains after the tokenizer's rules. Not necessarily a
word a human would underline.

**Type / term.** A distinct token string after normalization. `Alice`
and `alice` are one type under the Perl lowercaser.

**Vector space model.** Documents and queries as vectors over the same
term axes. TF-IDF supplies the coordinates; cosine (or a raw dot
product) supplies the angle.
