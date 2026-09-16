"""Split a handful of Gutenberg files into chapter- or book-sized units."""

from __future__ import annotations

import re
from pathlib import Path

from .index import Document

REPO_ROOT = Path(__file__).resolve().parents[1]
GUTENBERG = REPO_ROOT / "gutenberg"

ALICE_HEADING = re.compile(
    r"^\s*CHAPTER\s+([IVXLCDM]+|\d+)\.?\s*(.*)$"
)
MOBY_HEADING = re.compile(r"^CHAPTER\s+(\d+)\b(.*)$")
MILTON_HEADING = re.compile(r"^Book\s+([IVXLCDM]+)\s*$")
AUSTEN_HEADING = re.compile(r"^CHAPTER\s+([IVXLCDM]+)\s*$")


def _flush(
    units: list[Document],
    *,
    source: str,
    doc_id: str | None,
    title: str,
    lines: list[str],
) -> None:
    if not doc_id:
        return
    body = "\n".join(lines).strip()
    if not body:
        return
    units.append(Document(doc_id=doc_id, title=title, text=body, source=source))


def split_alice(text: str, source: str = "gutenberg/carroll-alice.txt") -> list[Document]:
    units: list[Document] = []
    doc_id: str | None = None
    title = ""
    lines: list[str] = []
    pending_title = False

    for raw in text.splitlines():
        match = ALICE_HEADING.match(raw)
        if match and (raw.lstrip().startswith("CHAPTER") or raw.startswith("CHAPTER")):
            numeral = match.group(1)
            rest = match.group(2).strip()
            _flush(units, source=source, doc_id=doc_id, title=title, lines=lines)
            slug = numeral.lower()
            doc_id = f"alice-{slug}"
            title = rest or f"Chapter {numeral}"
            lines = []
            pending_title = not rest
            continue
        if pending_title and raw.strip():
            title = raw.strip()
            pending_title = False
            continue
        if doc_id:
            lines.append(raw)

    _flush(units, source=source, doc_id=doc_id, title=title, lines=lines)
    return units


def split_moby(text: str, source: str = "gutenberg/melville-moby_dick.txt") -> list[Document]:
    units: list[Document] = []
    doc_id: str | None = None
    title = ""
    lines: list[str] = []

    for raw in text.splitlines():
        stripped = raw.strip()
        if stripped == "ETYMOLOGY.":
            _flush(units, source=source, doc_id=doc_id, title=title, lines=lines)
            doc_id = "moby-etymology"
            title = "Etymology"
            lines = []
            continue
        if stripped.startswith("EXTRACTS"):
            _flush(units, source=source, doc_id=doc_id, title=title, lines=lines)
            doc_id = "moby-extracts"
            title = "Extracts"
            lines = []
            continue
        match = MOBY_HEADING.match(raw)
        if match:
            number = match.group(1)
            rest = match.group(2).strip(" .-")
            _flush(units, source=source, doc_id=doc_id, title=title, lines=lines)
            doc_id = f"moby-{int(number):03d}"
            title = rest or f"Chapter {number}"
            lines = []
            continue
        if doc_id:
            lines.append(raw)

    _flush(units, source=source, doc_id=doc_id, title=title, lines=lines)
    return units


def split_milton(text: str, source: str = "gutenberg/milton-paradise.txt") -> list[Document]:
    units: list[Document] = []
    doc_id: str | None = None
    title = ""
    lines: list[str] = []

    for raw in text.splitlines():
        match = MILTON_HEADING.match(raw.rstrip())
        if match:
            numeral = match.group(1)
            _flush(units, source=source, doc_id=doc_id, title=title, lines=lines)
            doc_id = f"paradise-{numeral.lower()}"
            title = f"Book {numeral}"
            lines = []
            continue
        if doc_id:
            lines.append(raw)

    _flush(units, source=source, doc_id=doc_id, title=title, lines=lines)
    return units


def split_austen_chapters(
    text: str, *, book: str, source: str
) -> list[Document]:
    units: list[Document] = []
    doc_id: str | None = None
    title = ""
    lines: list[str] = []

    for raw in text.splitlines():
        match = AUSTEN_HEADING.match(raw.strip())
        if match:
            numeral = match.group(1)
            _flush(units, source=source, doc_id=doc_id, title=title, lines=lines)
            doc_id = f"{book}-{numeral.lower()}"
            title = f"Chapter {numeral}"
            lines = []
            continue
        if doc_id:
            lines.append(raw)

    _flush(units, source=source, doc_id=doc_id, title=title, lines=lines)
    return units


SPLITTERS = {
    "carroll-alice": lambda text: split_alice(text, "gutenberg/carroll-alice.txt"),
    "melville-moby_dick": lambda text: split_moby(text, "gutenberg/melville-moby_dick.txt"),
    "milton-paradise": lambda text: split_milton(text, "gutenberg/milton-paradise.txt"),
    "austen-emma": lambda text: split_austen_chapters(
        text, book="emma", source="gutenberg/austen-emma.txt"
    ),
    "austen-persuasion": lambda text: split_austen_chapters(
        text, book="persuasion", source="gutenberg/austen-persuasion.txt"
    ),
    "austen-sense": lambda text: split_austen_chapters(
        text, book="sense", source="gutenberg/austen-sense.txt"
    ),
}


def load_chapters(stem: str, path: Path | None = None) -> list[Document]:
    if stem not in SPLITTERS:
        known = ", ".join(sorted(SPLITTERS))
        raise KeyError(f"no chapter splitter for {stem!r}; known: {known}")
    target = path or (GUTENBERG / f"{stem}.txt")
    text = target.read_text(encoding="utf-8", errors="replace")
    return SPLITTERS[stem](text)
