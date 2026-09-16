#!/usr/bin/env python3
"""Run every reading-companion ``--check`` in one process."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import boilerplate_scan  # noqa: E402
import cosine_map  # noqa: E402
import folio_spellings  # noqa: E402
import length_study  # noqa: E402
import query_shelf  # noqa: E402
import term_atlas  # noqa: E402

CHECKS = (
    ("cosine_map", cosine_map.main),
    ("length_study", length_study.main),
    ("folio_spellings", folio_spellings.main),
    ("query_shelf", query_shelf.main),
    ("term_atlas", term_atlas.main),
    ("boilerplate_scan", boilerplate_scan.main),
)


def main(argv: list[str] | None = None) -> int:
    del argv  # reserved so the other CLIs stay consistent
    failed = 0
    for label, func in CHECKS:
        code = func(["--check"])
        if code != 0:
            print(f"FAILED {label}", file=sys.stderr)
            failed += 1
    if failed:
        print(f"{failed} check group(s) failed", file=sys.stderr)
        return 1
    print("all reading-companion checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
