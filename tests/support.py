"""Shared paths for the example tests."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
PYTHON_EXAMPLES = ROOT / "examples" / "python"
TINY_DOCS = ROOT / "examples" / "tiny-corpus" / "docs"
TINY_EXPECTED = ROOT / "examples" / "tiny-corpus" / "expected"
OUTPUT = ROOT / "output"
GUTENBERG = ROOT / "gutenberg"

if str(PYTHON_EXAMPLES) not in sys.path:
    sys.path.insert(0, str(PYTHON_EXAMPLES))
