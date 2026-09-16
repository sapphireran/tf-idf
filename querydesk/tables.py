"""Read and write the 2012 TSV tables."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Mapping


def load_tf_tsv(path: Path) -> dict[str, float]:
    values: dict[str, float] = {}
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.rstrip("\n")
            if not line:
                continue
            term, raw = line.split("\t", 1)
            values[term] = float(raw)
    return values


def load_df_tsv(path: Path) -> dict[str, int]:
    df: dict[str, int] = {}
    with path.open(encoding="utf-8", errors="replace") as handle:
        header = handle.readline()
        if not header.lower().startswith("word"):
            handle.seek(0)
        for line in handle:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 2:
                continue
            term, count = parts[0], parts[1]
            try:
                df[term] = int(count)
            except ValueError:
                continue
    return df


def write_tf_tsv(path: Path, values: Mapping[str, float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"{term}\t{values[term]}\n" for term in sorted(values)]
    path.write_text("".join(lines), encoding="utf-8")


def write_df_tsv(
    path: Path, df: Mapping[str, int], members: Mapping[str, Iterable[str]]
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    chunks = ["word \t #docs it exists in \t doc names\n"]
    for term in sorted(df):
        names = ", ".join(members[term])
        if names:
            names = names + ", "
        chunks.append(f"{term}\t{df[term]}\t{names}\n")
    path.write_text("".join(chunks), encoding="utf-8")


def list_table_files(directory: Path) -> list[Path]:
    return sorted(
        path
        for path in directory.iterdir()
        if path.is_file() and not path.name.startswith(".")
    )
