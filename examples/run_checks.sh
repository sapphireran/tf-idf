#!/usr/bin/env bash
# Recreate the tiny-corpus tables, score the excerpts, rank Alice, run unit tests.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

python3 examples/python/tfidf_example.py \
  --input-dir examples/tiny-corpus/docs \
  --output-dir /tmp/tiny-tfidf

diff -u examples/tiny-corpus/expected/idf.txt /tmp/tiny-tfidf/idf.txt
diff -ur examples/tiny-corpus/expected/tf /tmp/tiny-tfidf/tf
diff -ur examples/tiny-corpus/expected/tfidf /tmp/tiny-tfidf/tfidf

python3 examples/python/tfidf_example.py \
  --input-dir examples/excerpts \
  --output-dir /tmp/excerpt-tfidf

python3 examples/python/extract_top_terms.py /tmp/excerpt-tfidf/tfidf/alice-opening.txt -n 5
python3 examples/python/extract_top_terms.py output/tfidf/carroll-alice.txt -n 5

python3 -m unittest discover -s examples/python -p 'test_*.py'

echo "all example checks passed"
