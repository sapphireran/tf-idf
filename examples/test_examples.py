#!/usr/bin/env python3
"""Checks for the personal example helpers. Run from the repo root:

    python3 examples/test_examples.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RANK = ROOT / "examples" / "rank_terms.py"
TINY = ROOT / "examples" / "tiny-corpus" / "run_tfidf.py"


def run(args: list[str]) -> str:
    proc = subprocess.run(args, cwd=ROOT, check=True, capture_output=True, text=True)
    return proc.stdout


def test_tiny_corpus() -> None:
    out = run([sys.executable, str(TINY), "--check"])
    if "CHECK PASSED" not in out:
        raise AssertionError(out)
    if "0.154033" not in out:
        raise AssertionError(f"missing moth identity in\n{out}")


def test_rank_alice() -> None:
    out = run(
        [
            sys.executable,
            str(RANK),
            str(ROOT / "output" / "tfidf" / "carroll-alice.txt"),
            "-n",
            "5",
        ]
    )
    lines = [line for line in out.splitlines() if line and not line.startswith("-") and "score" not in line]
    # first data row after the header block
    data = [line for line in out.splitlines() if line.startswith("alice ")]
    if not data:
        raise AssertionError(f"alice is not the top ranked term:\n{out}")
    if "0.02595678" not in data[0]:
        raise AssertionError(f"unexpected alice score:\n{data[0]}")


def test_rank_moby_versus_alice() -> None:
    out = run(
        [
            sys.executable,
            str(RANK),
            str(ROOT / "output" / "tfidf" / "melville-moby_dick.txt"),
            "--versus",
            str(ROOT / "output" / "tfidf" / "carroll-alice.txt"),
            "-n",
            "8",
        ]
    )
    if "whale" not in out or "ahab" not in out:
        raise AssertionError(out)
    if "absent" not in out:
        raise AssertionError(f"expected some Moby terms to be absent from Alice:\n{out}")


def main() -> int:
    tests = [test_tiny_corpus, test_rank_alice, test_rank_moby_versus_alice]
    failed = 0
    for fn in tests:
        try:
            fn()
        except Exception as exc:  # noqa: BLE001 — keep the runner tiny
            failed += 1
            print(f"FAIL {fn.__name__}: {exc}")
        else:
            print(f"ok   {fn.__name__}")
    if failed:
        print(f"{failed} failed")
        return 1
    print(f"{len(tests)} passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
