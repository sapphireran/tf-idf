"""Make ``tfidfkit`` importable when the CLIs are run as scripts."""

from __future__ import annotations

import sys
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
if str(PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGE_DIR))

REPO_ROOT = PACKAGE_DIR.parents[1]
