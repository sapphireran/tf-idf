"""A short personal English stoplist for top-term browsing.

This is not a linguistic resource. It exists so smoothed-IDF listings
are readable. Do not use it when reproducing the 2012 tables.
"""

from __future__ import annotations

from typing import FrozenSet

# Deliberately small. I add a word here only when it has annoyed me
# twice in a top-terms listing.
ENGLISH_STUDY: FrozenSet[str] = frozenset(
    """
    a an the and or but if then else
    of to in on at by for from with into onto over
    is are was were be been being
    it its this that these those
    i you he she we they them his her our their
    not no nor
    as so than too very
    do did does done doing
    have has had having
    will would can could should may might must
    mr mrs miss ms
    said says say
    """.split()
)
