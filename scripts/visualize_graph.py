"""Renders the LangGraph topology as ASCII, Mermaid (.mmd) and PNG into docs/.

Run from the repo root:  uv run python -m scripts.visualize_graph
"""

from pathlib import Path

from apps.orchestrator.graph import app_graph

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = REPO_ROOT / "docs"


def main():
    print("\n" + "=" * 70)
    print("   TRIALGUARD ORCHESTRATOR WORKFLOW GRAPH (ASCII, MERMAID & PNG)")
    print("=" * 70 + "\n")

    graph_drawable = app_graph.get_graph()

    # -------------------------------------------------------------------
    # 1. Terminal ASCII Topology
    # -------------------------------------------------------------------
    try:
        graph_drawable.print_ascii()
    except Exception as exc:
        print(f"[Notice] ASCII render fallback: {exc}")

    # -------------------------------------------------------------------
    # 2. Output Raw Mermaid Definition (.mmd)
    # -------------------------------------------------------------------
    mmd_path = DOCS_DIR / "orchestrator_graph.mmd"
    try:
        mermaid_code = graph_drawable.draw_mermaid()
        mmd_path.write_text(mermaid_code, encoding="utf-8")
        print(f"\n✓ Exported Mermaid specification: {mmd_path.name}")
    except Exception as exc:
        print(f"\n[Warning] Could not export Mermaid source: {exc}")

    # -------------------------------------------------------------------
    # 3. Export Rendered Visual Diagram (.png)
    # -------------------------------------------------------------------
    out_path = DOCS_DIR / "orchestrator_graph.png"
    try:
        png_bytes = graph_drawable.draw_mermaid_png()
        out_path.write_bytes(png_bytes)
        print(f"✓ Saved compiled visual pipeline to : {out_path.name}")
        print(f"  Path: {out_path.resolve()}\n")
    except Exception as exc:
        print(f"\n[Note] Mermaid PNG generation skipped: {exc}")
        print("Tip: Remote PNG rendering requires internet access or pygraphviz / mermaid-cli.")
        if mmd_path.exists():
            print(f"     View online by pasting '{mmd_path.name}' contents into https://mermaid.live")


if __name__ == "__main__":
    main()