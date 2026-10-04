import sys
from pathlib import Path

# Resolve workspace layout dynamically
ROOT_DIR = Path(__file__).resolve().parent
REPO_ROOT = ROOT_DIR if (ROOT_DIR / "apps").exists() else ROOT_DIR.parents[1]

# Path injection for monorepo cross-package resolution
PATHS = [
    REPO_ROOT,
    REPO_ROOT / "apps" / "orchestrator",
    REPO_ROOT / "apps" / "agent_master",
    REPO_ROOT / "apps" / "agent-master",
    REPO_ROOT / "packages" / "mcp-ehr" / "src" / "mcp_ehr",
    REPO_ROOT / "packages" / "mcp-ehr" / "src",
    REPO_ROOT / "packages" / "shared-schemas",
]

for p in PATHS:
    if p.exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

try:
    from apps.orchestrator.graph import app_graph
except ImportError:
    try:
        from graph import app_graph
    except ImportError:
        from apps.orchestrator.graph import build_graph
        app_graph = build_graph()


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
    mmd_path = REPO_ROOT / "orchestrator_graph.mmd"
    try:
        mermaid_code = graph_drawable.draw_mermaid()
        mmd_path.write_text(mermaid_code, encoding="utf-8")
        print(f"\n✓ Exported Mermaid specification: {mmd_path.name}")
    except Exception as exc:
        print(f"\n[Warning] Could not export Mermaid source: {exc}")

    # -------------------------------------------------------------------
    # 3. Export Rendered Visual Diagram (.png)
    # -------------------------------------------------------------------
    out_path = REPO_ROOT / "orchestrator_graph.png"
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