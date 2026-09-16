"""Load the original personal commonplace-book notes."""

from __future__ import annotations

from pathlib import Path

from .index import Document, TfIdfIndex

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DIR = REPO_ROOT / "examples" / "commonplace"


def load_commonplace(directory: Path | None = None) -> list[Document]:
    root = directory or DEFAULT_DIR
    docs: list[Document] = []
    for path in sorted(root.glob("*.txt")):
        text = path.read_text(encoding="utf-8")
        title = text.splitlines()[0].lstrip("# ").strip() if text.strip() else path.stem
        docs.append(
            Document(
                doc_id=path.stem,
                title=title,
                text=text,
                source=str(path.relative_to(REPO_ROOT)),
            )
        )
    if not docs:
        raise FileNotFoundError(f"no commonplace notes in {root}")
    return docs


def commonplace_index(
    directory: Path | None = None, *, idf_mode: str = "classic"
) -> TfIdfIndex:
    return TfIdfIndex(load_commonplace(directory), idf_mode=idf_mode)  # type: ignore[arg-type]
