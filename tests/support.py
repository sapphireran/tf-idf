"""Shared paths for the teaching-implementation tests."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON_EXAMPLES = ROOT / "examples" / "python"
MICRO = ROOT / "examples" / "micro-corpus"
TINY = ROOT / "examples" / "tiny-corpus"
GUTENBERG_TFIDF = ROOT / "output" / "tfidf"

if str(PYTHON_EXAMPLES) not in sys.path:
    sys.path.insert(0, str(PYTHON_EXAMPLES))
