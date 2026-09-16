"""Read and write the TSV layouts used under ``output/``."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable

_FLOAT_PREFIX = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?")


@dataclass(frozen=True)
class WeightedDocument:
    name: str
    weights: dict[str, float]


@dataclass
class CommittedTables:
    """The frozen 2012 snapshot, loaded from ``output/``."""

    df: dict[str, tuple[int, tuple[str, ...]]]
    idf: dict[str, float]
    dirty_idf: tuple[str, ...]
    tf: dict[str, dict[str, float]]
    tfidf: dict[str, dict[str, float]]


def parse_idf_value(raw: str) -> tuple[float, bool]:
    """Parse an ``idf`` cell.

    Returns ``(value, dirty)``. The committed snapshot has one cell,
    ``2.89037175789616y``, whose leading float is usable.
    """
    text = raw.strip()
    try:
        return float(text), False
    except ValueError:
        match = _FLOAT_PREFIX.match(text)
        if not match:
            raise ValueError(f"not a float: {raw!r}") from None
        return float(match.group(0)), True


def read_token_weights(path: Path) -> dict[str, float]:
    weights: dict[str, float] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) != 2:
            raise ValueError(f"{path}:{line_number}: expected token<TAB>value")
        value, _dirty = parse_idf_value(parts[1])
        weights[parts[0]] = value
    return weights


def read_weighted_dir(directory: Path) -> dict[str, dict[str, float]]:
    tables: dict[str, dict[str, float]] = {}
    for path in sorted(directory.glob("*.txt")):
        if path.name.startswith("."):
            continue
        tables[path.name] = read_token_weights(path)
    return tables


def read_idf(path: Path) -> tuple[dict[str, float], tuple[str, ...]]:
    idf: dict[str, float] = {}
    dirty: list[str] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) != 2:
            raise ValueError(f"{path}:{line_number}: expected token<TAB>idf")
        value, is_dirty = parse_idf_value(parts[1])
        idf[parts[0]] = value
        if is_dirty:
            dirty.append(parts[0])
    return idf, tuple(dirty)


def read_df(path: Path) -> dict[str, tuple[int, tuple[str, ...]]]:
    """Read ``output/df.txt``.

    Returns ``token -> (df, posting_list)``. The header line is skipped.
    """
    rows: dict[str, tuple[int, tuple[str, ...]]] = {}
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        return rows
    start = 1 if lines[0].lower().startswith("word") else 0
    for line_number, line in enumerate(lines[start:], start=start + 1):
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            raise ValueError(f"{path}:{line_number}: expected token<TAB>df")
        token = parts[0]
        df_count = int(parts[1])
        names: tuple[str, ...] = ()
        if len(parts) >= 3:
            names = tuple(
                name.strip() for name in parts[2].split(",") if name.strip()
            )
        rows[token] = (df_count, names)
    return rows


def write_token_weights(path: Path, weights: dict[str, float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"{token}\t{weights[token]}\n" for token in sorted(weights)]
    path.write_text("".join(lines), encoding="utf-8")


def write_df(path: Path, df: dict[str, set[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["word\t#docs it exists in\tdoc names\n"]
    for token in sorted(df):
        names = ", ".join(sorted(df[token]))
        lines.append(f"{token}\t{len(df[token])}\t{names},\n")
    path.write_text("".join(lines), encoding="utf-8")


def write_pipeline_tree(output_dir: Path, tf, df, idf, tfidf) -> None:
    """Write the four-table layout used under ``output/``."""
    tf_dir = output_dir / "tf"
    tfidf_dir = output_dir / "tfidf"
    for name, weights in tf.items():
        write_token_weights(tf_dir / name, weights)
    for name, weights in tfidf.items():
        write_token_weights(tfidf_dir / name, weights)
    write_df(output_dir / "df.txt", df)
    write_token_weights(output_dir / "idf.txt", idf)


def load_committed(output_dir: Path) -> CommittedTables:
    idf, dirty = read_idf(output_dir / "idf.txt")
    return CommittedTables(
        df=read_df(output_dir / "df.txt"),
        idf=idf,
        dirty_idf=dirty,
        tf=read_weighted_dir(output_dir / "tf"),
        tfidf=read_weighted_dir(output_dir / "tfidf"),
    )


def iter_ranked(weights: dict[str, float]) -> Iterable[tuple[str, float]]:
    return sorted(weights.items(), key=lambda item: (-item[1], item[0]))
