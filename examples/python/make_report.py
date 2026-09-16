#!/usr/bin/env python3
"""Write a standalone HTML report for a scored document directory."""

from __future__ import annotations

import argparse
import html
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from tfidf_lab import build_index, build_worked_example, load_documents


def _esc(value: object) -> str:
    return html.escape(str(value))


def render(index, worked_rows=None) -> str:
    names = [doc.name for doc in index.documents]
    vocab_rows = []
    for term in index.vocabulary():
        stat = index.stats[term]
        vocab_rows.append(
            "<tr>"
            f"<td>{_esc(term)}</td>"
            f"<td>{stat.df}</td>"
            f"<td>{stat.idf:.6f}</td>"
            f"<td>{_esc(', '.join(stat.documents))}</td>"
            "</tr>"
        )

    doc_sections = []
    for doc in index.documents:
        chips = []
        for term, score in index.scored[doc.name].top_terms(10):
            chips.append(
                f"<li><code>{_esc(term)}</code> <span>{score:.6f}</span></li>"
            )
        excerpt = doc.text.strip()
        doc_sections.append(
            "<article class='doc'>"
            f"<h3>{_esc(doc.name)}</h3>"
            f"<p class='meta'>{doc.length} tokens · "
            f"{len(index.scored[doc.name].tf)} unique terms</p>"
            f"<p class='excerpt'>{_esc(excerpt)}</p>"
            f"<ol>{''.join(chips)}</ol>"
            "</article>"
        )

    sim_header = "".join(f"<th>{_esc(name)}</th>" for name in names)
    sim_rows = []
    for left in names:
        cells = [f"<th>{_esc(left)}</th>"]
        for right in names:
            score = index.cosine(left, right)
            cells.append(f"<td>{score:.3f}</td>")
        sim_rows.append(f"<tr>{''.join(cells)}</tr>")

    worked_html = ""
    if worked_rows:
        body = []
        for row in worked_rows:
            body.append(
                "<tr>"
                f"<td>{_esc(row.document)}</td>"
                f"<td>{_esc(row.term)}</td>"
                f"<td>{row.count}</td>"
                f"<td>{row.length}</td>"
                f"<td>{row.tf:.6f}</td>"
                f"<td>{row.df}</td>"
                f"<td>{row.idf:.6f}</td>"
                f"<td>{row.tfidf:.6f}</td>"
                "</tr>"
            )
        worked_html = f"""
        <section>
          <h2>Hand-checkable classroom example</h2>
          <p>Three sentences, every cell expanded. Formula:
          <code>tf = count / length</code>,
          <code>idf = ln(N / df)</code>,
          <code>tfidf = tf × idf</code>, with <code>N = 3</code>.</p>
          <table>
            <thead>
              <tr>
                <th>doc</th><th>term</th><th>count</th><th>len</th>
                <th>tf</th><th>df</th><th>idf</th><th>tf-idf</th>
              </tr>
            </thead>
            <tbody>{''.join(body)}</tbody>
          </table>
        </section>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Personal tf-idf lab report</title>
  <style>
    :root {{
      --ink: #1b1b18;
      --paper: #f6f1e7;
      --card: #fffdf8;
      --line: #d7cbb3;
      --accent: #6b3f1d;
    }}
    body {{
      margin: 0;
      font: 16px/1.5 "Iowan Old Style", "Palatino Linotype", Palatino, serif;
      color: var(--ink);
      background: var(--paper);
    }}
    main {{ max-width: 980px; margin: 0 auto; padding: 2.5rem 1.25rem 4rem; }}
    h1, h2, h3 {{ font-weight: 650; letter-spacing: -0.02em; }}
    h1 {{ font-size: 2rem; margin-bottom: 0.25rem; }}
    .lede {{ color: #4a4338; max-width: 40rem; }}
    .grid {{ display: grid; gap: 1rem; }}
    @media (min-width: 800px) {{
      .grid.docs {{ grid-template-columns: 1fr 1fr; }}
    }}
    article.doc, table {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 12px;
    }}
    article.doc {{ padding: 1rem 1.1rem 0.4rem; }}
    article.doc h3 {{ margin: 0 0 0.2rem; color: var(--accent); }}
    .meta {{ color: #6a6256; font-size: 0.9rem; margin-top: 0; }}
    .excerpt {{ white-space: pre-wrap; font-size: 0.95rem; }}
    ol {{ padding-left: 1.2rem; }}
    ol li {{ margin: 0.15rem 0; }}
    code {{ font-family: ui-monospace, "Source Code Pro", monospace; font-size: 0.92em; }}
    table {{ border-collapse: collapse; width: 100%; overflow: hidden; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 0.4rem 0.55rem; text-align: left; }}
    th {{ background: #efe6d4; }}
    .scroll {{ overflow-x: auto; }}
  </style>
</head>
<body>
  <main>
    <h1>Personal tf-idf lab report</h1>
    <p class="lede">
      Variant <code>{_esc(index.variant)}</code> on
      {index.n_documents} original short documents.
      Scores use the same product as this repository:
      term frequency as a within-document proportion, times
      <code>ln(N / df)</code>.
    </p>
    {worked_html}
    <section>
      <h2>Documents and distinctive terms</h2>
      <div class="grid docs">{''.join(doc_sections)}</div>
    </section>
    <section>
      <h2>Pairwise cosine similarity</h2>
      <div class="scroll">
        <table>
          <thead><tr><th></th>{sim_header}</tr></thead>
          <tbody>{''.join(sim_rows)}</tbody>
        </table>
      </div>
    </section>
    <section>
      <h2>Collection vocabulary</h2>
      <div class="scroll">
        <table>
          <thead>
            <tr><th>term</th><th>df</th><th>idf</th><th>documents</th></tr>
          </thead>
          <tbody>{''.join(vocab_rows)}</tbody>
        </table>
      </div>
    </section>
  </main>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--docs",
        type=Path,
        default=ROOT / "examples" / "tiny_corpus" / "docs",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "examples" / "tiny_corpus" / "expected" / "report.html",
    )
    parser.add_argument("--include-worked", action="store_true")
    args = parser.parse_args()

    index = build_index(load_documents(args.docs))
    worked_rows = build_worked_example().rows if args.include_worked else None
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render(index, worked_rows), encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
