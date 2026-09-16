"""Human-readable markdown reports for the example corpora."""

from __future__ import annotations

from .compute import TfidfIndex, format_top_table, pairwise_cosine, score_query


def render_corpus_report(
    index: TfidfIndex,
    *,
    top_n: int = 8,
    query: str | None = None,
) -> str:
    """Build a markdown report: corpus size, top terms, similarities, optional query."""
    sections = [
        "# TF-IDF report",
        "",
        f"- documents: **{index.n_documents}**",
        f"- vocabulary: **{len(index.idf)}** terms",
        f"- IDF mode: `{index.idf_mode}`",
        "",
        "A term that appears in every document has raw IDF `log(1) = 0`, so it",
        "drops out of TF-IDF. Distinctive names and rare nouns rise to the top.",
        "",
    ]
    for doc in index.documents:
        sections.append(f"## {doc.name}")
        sections.append("")
        sections.append(f"{doc.token_count} tokens after cleanup.")
        sections.append("")
        sections.append(format_top_table(doc.top_terms(top_n)))
        sections.append("")

    pairs = pairwise_cosine(index)
    if pairs:
        sections.extend(
            [
                "## Pairwise cosine similarity",
                "",
                "Computed on the sparse TF-IDF vectors (not on raw counts).",
                "",
                "| left | right | cosine |",
                "| --- | --- | ---: |",
            ]
        )
        for left, right, score in pairs:
            sections.append(f"| {left} | {right} | {score:.4f} |")
        sections.append("")

    if query:
        ranked = score_query(index, query)
        sections.extend(
            [
                f"## Query ranking: `{query}`",
                "",
                "Query terms missing from the corpus IDF table are ignored.",
                "",
                "| document | cosine vs query |",
                "| --- | ---: |",
            ]
        )
        for name, score in ranked:
            sections.append(f"| {name} | {score:.4f} |")
        sections.append("")

    return "\n".join(sections).rstrip() + "\n"


def render_existing_top_terms(
    tables: list[tuple[str, dict[str, float]]],
    *,
    top_n: int = 10,
) -> str:
    """Markdown report from already-written TF-IDF TSV files (the Gutenberg dump)."""
    sections = [
        "# Top TF-IDF terms from existing tables",
        "",
        "These scores were read from TSV files; nothing was recomputed.",
        "",
    ]
    for name, weights in tables:
        ranked = sorted(weights.items(), key=lambda item: (-item[1], item[0]))[:top_n]
        sections.append(f"## {name}")
        sections.append("")
        sections.append(format_top_table(ranked))
        sections.append("")
    return "\n".join(sections).rstrip() + "\n"
