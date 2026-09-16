"""Read and write the tab-separated tables produced by the original Perl scripts."""

from __future__ import annotations

from pathlib import Path

from .compute import TfidfIndex


def write_weight_table(path: str | Path, weights: dict[str, float]) -> None:
    """Write ``term<TAB>value`` lines, terms sorted alphabetically."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"{term}\t{weights[term]}\n" for term in sorted(weights)]
    destination.write_text("".join(lines), encoding="utf-8")


def read_weight_table(path: str | Path) -> dict[str, float]:
    """Read a ``term<TAB>value`` table. Blank lines are ignored."""
    weights: dict[str, float] = {}
    for raw_line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip("\n")
        if not line.strip():
            continue
        term, sep, rest = line.partition("\t")
        if not sep:
            raise ValueError(f"expected a tab in {path}: {raw_line!r}")
        weights[term] = float(rest)
    return weights


def write_df_table(path: str | Path, index: TfidfIndex) -> None:
    """Write the three-column document-frequency listing."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    lines = ["word \t #docs it exists in \t doc names\n"]
    for term in sorted(index.df):
        names = ", ".join(f"{name}" for name in index.docs_for_term[term])
        lines.append(f"{term}\t{index.df[term]}\t{names}, \n")
    destination.write_text("".join(lines), encoding="utf-8")


def write_pipeline_output(index: TfidfIndex, output_dir: str | Path) -> Path:
    """Write ``tf/``, ``idf.txt``, ``df.txt``, and ``tfidf/`` under ``output_dir``."""
    root = Path(output_dir)
    (root / "tf").mkdir(parents=True, exist_ok=True)
    (root / "tfidf").mkdir(parents=True, exist_ok=True)
    write_weight_table(root / "idf.txt", index.idf)
    write_df_table(root / "df.txt", index)
    for doc in index.documents:
        write_weight_table(root / "tf" / doc.name, doc.tf)
        write_weight_table(root / "tfidf" / doc.name, doc.tfidf)
    return root


def load_existing_tfidf_dir(tfidf_dir: str | Path) -> list[tuple[str, dict[str, float]]]:
    """Load every non-hidden TSV in a directory of already-computed TF-IDF files."""
    root = Path(tfidf_dir)
    if not root.is_dir():
        raise FileNotFoundError(f"TF-IDF directory not found: {root}")
    tables: list[tuple[str, dict[str, float]]] = []
    for path in sorted(root.iterdir(), key=lambda item: item.name):
        if not path.is_file() or path.name.startswith("."):
            continue
        tables.append((path.name, read_weight_table(path)))
    if not tables:
        raise ValueError(f"no TF-IDF tables found in {root}")
    return tables
