"""Split the NLTK / Gutenberg King James file into named books.

The checked-in ``gutenberg/bible-kjv.txt`` is one 821k-word blob. Most
Protestant books have a title line; a few have an "Otherwise Called" or
"Commonly Called" alias on the next line that must not start a new book.
The twelve minor prophets (Hosea through Malachi) have no titles in this
particular dump, so they are kept as a single unit ``hosea-malachi``.

That limitation is the point of the study note: TF-IDF can only be as
sharp as the document boundaries you give it.
"""

from __future__ import annotations

from pathlib import Path

from .index import Document

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BIBLE = REPO_ROOT / "gutenberg" / "bible-kjv.txt"

# Primary title lines, in canonical Protestant order. 1 Kings and 2 Kings
# both open with "The First Book of the Kings" in this file; the splitter
# consumes those two occurrences in order after skipping alias lines.
BOOK_HEADERS: list[tuple[str, str]] = [
    ("genesis", "The First Book of Moses:  Called Genesis"),
    ("exodus", "The Second Book of Moses:  Called Exodus"),
    ("leviticus", "The Third Book of Moses:  Called Leviticus"),
    ("numbers", "The Fourth Book of Moses:  Called Numbers"),
    ("deuteronomy", "The Fifth Book of Moses:  Called Deuteronomy"),
    ("joshua", "The Book of Joshua"),
    ("judges", "The Book of Judges"),
    ("ruth", "The Book of Ruth"),
    ("1-samuel", "The First Book of Samuel"),
    ("2-samuel", "The Second Book of Samuel"),
    ("1-kings", "The First Book of the Kings"),
    ("2-kings", "The First Book of the Kings"),
    ("1-chronicles", "The First Book of the Chronicles"),
    ("2-chronicles", "The Second Book of the Chronicles"),
    ("ezra", "Ezra"),
    ("nehemiah", "The Book of Nehemiah"),
    ("esther", "The Book of Esther"),
    ("job", "The Book of Job"),
    ("psalms", "The Book of Psalms"),
    ("proverbs", "The Proverbs"),
    ("ecclesiastes", "The Preacher"),
    ("song-of-solomon", "The Song of Solomon"),
    ("isaiah", "The Book of the Prophet Isaiah"),
    ("jeremiah", "The Book of the Prophet Jeremiah"),
    ("lamentations", "The Lamentations of Jeremiah"),
    ("ezekiel", "The Book of the Prophet Ezekiel"),
    ("daniel", "The Book of Daniel"),
    ("matthew", "The Gospel According to Saint Matthew"),
    ("mark", "The Gospel According to Saint Mark"),
    ("luke", "The Gospel According to Saint Luke"),
    ("john", "The Gospel According to Saint John"),
    ("acts", "The Acts of the Apostles"),
    ("romans", "The Epistle of Paul the Apostle to the Romans"),
    ("1-corinthians", "The First Epistle of Paul the Apostle to the Corinthians"),
    ("2-corinthians", "The Second Epistle of Paul the Apostle to the Corinthians"),
    ("galatians", "The Epistle of Paul the Apostle to the Galatians"),
    ("ephesians", "The Epistle of Paul the Apostle to the Ephesians"),
    ("philippians", "The Epistle of Paul the Apostle to the Philippians"),
    ("colossians", "The Epistle of Paul the Apostle to the Colossians"),
    ("1-thessalonians", "The First Epistle of Paul the Apostle to the Thessalonians"),
    ("2-thessalonians", "The Second Epistle of Paul the Apostle to the Thessalonians"),
    ("1-timothy", "The First Epistle of Paul the Apostle to Timothy"),
    ("2-timothy", "The Second Epistle of Paul the Apostle to Timothy"),
    ("titus", "The Epistle of Paul the Apostle to Titus"),
    ("philemon", "The Epistle of Paul the Apostle to Philemon"),
    ("hebrews", "The Epistle of Paul the Apostle to the Hebrews"),
    ("james", "The General Epistle of James"),
    ("1-peter", "The First Epistle General of Peter"),
    ("2-peter", "The Second General Epistle of Peter"),
    ("1-john", "The First Epistle General of John"),
    ("2-john", "The Second Epistle General of John"),
    ("3-john", "The Third Epistle General of John"),
    ("jude", "The General Epistle of Jude"),
    ("revelation", "The Revelation of Saint John the Devine"),
]

SECTION_BANNERS = {
    "[The King James Bible]",
    "The Old Testament of the King James Bible",
    "The New Testament of the King James Bible",
}
ALIAS_MARKERS = {"Otherwise Called:", "Commonly Called:"}
HOSEA_MALACHI_ID = "hosea-malachi"
HOSEA_MALACHI_TITLE = "Hosea–Malachi (untitled in this dump)"


def _header_lookup() -> dict[str, list[str]]:
    table: dict[str, list[str]] = {}
    for book_id, title in BOOK_HEADERS:
        table.setdefault(title, []).append(book_id)
    return table


def split_bible_text(text: str) -> list[Document]:
    """Return one Document per titled book, plus the untitled minor-prophet run."""
    header_ids = _header_lookup()
    remaining: dict[str, list[str]] = {title: ids[:] for title, ids in header_ids.items()}

    books: list[Document] = []
    current_id: str | None = None
    current_title = ""
    current_lines: list[str] = []
    skip_alias = False
    saw_daniel = False

    def flush() -> None:
        nonlocal current_id, current_title, current_lines
        if current_id is None:
            current_lines = []
            return
        body = "\n".join(current_lines).strip()
        if body:
            books.append(
                Document(
                    doc_id=current_id,
                    title=current_title,
                    text=body,
                    source="gutenberg/bible-kjv.txt",
                )
            )
        current_id = None
        current_title = ""
        current_lines = []

    def start_book(book_id: str, title: str) -> None:
        nonlocal current_id, current_title, current_lines, saw_daniel
        flush()
        current_id = book_id
        current_title = title
        current_lines = []
        if book_id == "daniel":
            saw_daniel = True

    for raw in text.splitlines():
        stripped = raw.strip()
        if skip_alias:
            # Alias titles are often separated from "Otherwise Called:" by
            # a blank line in this dump. Skip empties until the title goes.
            if not stripped:
                continue
            skip_alias = False
            continue
        if stripped in ALIAS_MARKERS:
            skip_alias = True
            continue
        if stripped in SECTION_BANNERS:
            if saw_daniel and current_id == HOSEA_MALACHI_ID:
                flush()
            continue

        queued = remaining.get(stripped)
        if queued:
            book_id = queued.pop(0)
            if not queued:
                remaining.pop(stripped, None)
            start_book(book_id, stripped)
            continue

        if current_id is None:
            continue

        # After Daniel's body starts accumulating, the next non-header run
        # that no longer belongs to Daniel is detected only when Matthew
        # arrives — unless we split when verse numbering resets from a high
        # chapter back to 1:1 *and* we have already seen the end of Daniel.
        # The dump has no title, so we open hosea-malachi at the first 1:1
        # that appears after Daniel chapter 12 material.
        if current_id == "daniel" and _looks_like_minor_prophet_open(stripped, current_lines):
            flush()
            current_id = HOSEA_MALACHI_ID
            current_title = HOSEA_MALACHI_TITLE
            current_lines = [raw]
            continue

        current_lines.append(raw)

    flush()
    return books


def _looks_like_minor_prophet_open(stripped: str, daniel_lines: list[str]) -> bool:
    """Hosea begins at the first ``1:1`` after Daniel 12 has been seen."""
    if not stripped.startswith("1:1 "):
        return False
    joined = "\n".join(daniel_lines[-40:])
    return "12:" in joined or "Nebuchadnezzar" in joined


def load_bible(path: Path | None = None) -> list[Document]:
    target = path or DEFAULT_BIBLE
    return split_bible_text(target.read_text(encoding="utf-8", errors="replace"))


def expected_book_ids() -> list[str]:
    ids = [book_id for book_id, _ in BOOK_HEADERS]
    # Insert hosea-malachi after daniel.
    daniel_at = ids.index("daniel")
    return ids[: daniel_at + 1] + [HOSEA_MALACHI_ID] + ids[daniel_at + 1 :]
