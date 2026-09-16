"""Attribute Folio speech prefixes to named voices in the three plays.

The NLTK Shakespeare files keep First Folio spellings and abbreviated
speech prefixes (``Macb.``, ``La.``, ``Hor.``). This splitter is a study
tool, not a dramaturge: it walks lines, starts a new turn when a known
prefix appears, and folds aliases so ``Macb`` and ``Macbeth`` share a
document. Stage directions are skipped.

The resulting documents are *voices*, not scenes. That is a different
unit from the 2012 file-level tables, and the distinctive terms change
with it: witches keep ``heath`` and ``hurleyburley``, Lady Macbeth keeps
the unsexing vocabulary, Hamlet keeps ``horatio``.
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

from .index import Document

REPO_ROOT = Path(__file__).resolve().parents[1]
GUTENBERG = REPO_ROOT / "gutenberg"

SPEECH_PREFIX = re.compile(
    r"^(?P<indent>\s{0,3})(?P<name>[A-Z][A-Za-z]{0,16}|[1-3]|All|La)\.\s+(?P<rest>.*)$"
)
# Enter / scene banners start a new block. A lone "Exit Messenger."
# often sits in the middle of a Folio speech (Lady Macbeth after the
# letter, for example) and must not drop the current voice.
HARD_STAGE = re.compile(
    r"^\s*(Enter|Exeunt|Thunder|Alarum|Flourish|Sennet|"
    r"Actus|Scoena|Scena|Scene|Finis)\b",
    re.IGNORECASE,
)
SOFT_STAGE = re.compile(r"^\s*(Exit|Aside)\b", re.IGNORECASE)

ALIASES: dict[str, dict[str, str]] = {
    "shakespeare-macbeth": {
        "macb": "macbeth",
        "macbeth": "macbeth",
        "lady": "lady-macbeth",
        "la": "lady-macbeth",
        "macd": "macduff",
        "macduff": "macduff",
        "banq": "banquo",
        "ban": "banquo",
        "banquo": "banquo",
        "mal": "malcolm",
        "malc": "malcolm",
        "malcolm": "malcolm",
        "rosse": "rosse",
        "lenox": "lenox",
        "len": "lenox",
        "king": "duncan",
        "duncan": "duncan",
        "doct": "doctor",
        "doctor": "doctor",
        "wife": "macduff-wife",
        "son": "macduff-son",
        "1": "witches",
        "2": "witches",
        "3": "witches",
        "all": "witches",
        "sey": "seward",
        "ment": "menteth",
        "ang": "angus",
        "mes": "messenger",
    },
    "shakespeare-hamlet": {
        "ham": "hamlet",
        "hamlet": "hamlet",
        "hor": "horatio",
        "hora": "horatio",
        "horatio": "horatio",
        "king": "claudius",
        "queen": "gertrude",
        "qu": "gertrude",
        "pol": "polonius",
        "polonius": "polonius",
        "laer": "laertes",
        "laertes": "laertes",
        "oph": "ophelia",
        "ophelia": "ophelia",
        "gho": "ghost",
        "ghost": "ghost",
        "rosin": "rosencrantz",
        "rosincrant": "rosencrantz",
        "guild": "guildenstern",
        "guil": "guildenstern",
        "barnardo": "barnardo",
        "bar": "barnardo",
        "barn": "barnardo",
        "fran": "francisco",
        "fra": "francisco",
        "mar": "marcellus",
        "osr": "osric",
        "fortin": "fortinbras",
    },
    "shakespeare-caesar": {
        "brut": "brutus",
        "brutus": "brutus",
        "cassi": "cassius",
        "cassius": "cassius",
        "ant": "antony",
        "antony": "antony",
        "caes": "caesar",
        "caesar": "caesar",
        "casca": "casca",
        "cask": "casca",
        "octa": "octavius",
        "octavius": "octavius",
        "portia": "portia",
        "por": "portia",
        "decius": "decius",
        "cinna": "cinna",
        "luc": "lucius",
        "lucius": "lucius",
        "mess": "messenger",
        "sooth": "soothsayer",
        "cit": "citizen",
        "1": "citizen",
        "2": "citizen",
        "3": "citizen",
    },
}

PLAY_TITLES = {
    "shakespeare-macbeth": "Macbeth",
    "shakespeare-hamlet": "Hamlet",
    "shakespeare-caesar": "Julius Caesar",
}


def _canon(play: str, raw_name: str) -> str | None:
    key = raw_name.strip().lower().rstrip(".")
    table = ALIASES.get(play, {})
    return table.get(key)


def split_speakers(text: str, play: str) -> list[Document]:
    buckets: dict[str, list[str]] = defaultdict(list)
    current: str | None = None

    for raw in text.splitlines():
        if HARD_STAGE.match(raw):
            current = None
            continue
        if SOFT_STAGE.match(raw) or raw.strip() == "":
            continue
        match = SPEECH_PREFIX.match(raw)
        if match:
            canon = _canon(play, match.group("name"))
            if canon is None:
                current = None
                continue
            current = canon
            rest = match.group("rest").strip()
            if rest:
                buckets[current].append(rest)
            continue
        # Folio verse often wraps to column 0 with a capital letter.
        # Stay with the current voice until a blank, a stage direction,
        # or a new speech prefix.
        if current:
            buckets[current].append(raw.strip())
            continue
        current = None

    play_title = PLAY_TITLES.get(play, play)
    docs: list[Document] = []
    for voice, lines in sorted(buckets.items()):
        body = " ".join(line for line in lines if line)
        if len(body.split()) < 20:
            continue
        docs.append(
            Document(
                doc_id=f"{play}:{voice}",
                title=f"{play_title} / {voice}",
                text=body,
                source=f"gutenberg/{play}.txt",
            )
        )
    return docs


def load_speakers(play: str, path: Path | None = None) -> list[Document]:
    if play not in ALIASES:
        known = ", ".join(sorted(ALIASES))
        raise KeyError(f"no speaker map for {play!r}; known: {known}")
    target = path or (GUTENBERG / f"{play}.txt")
    return split_speakers(
        target.read_text(encoding="utf-8", errors="replace"), play
    )
