"""Visualization plugin — tree rendering (ASCII preview + ggtree for publication figures)."""

import shutil
import subprocess
import tempfile
from pathlib import Path

from ..core.plugin import Plugin, PluginResult


def _find_rscript() -> str | None:
    for name in ["Rscript.exe", "Rscript"]:
        p = shutil.which(name)
        if p:
            return p
    return None


def _ascii_tree(newick: str, width: int = 60) -> str:
    """Render a simple ASCII tree from newick string."""
    newick = newick.strip().rstrip(";")

    def _clean(name: str) -> str:
        """Strip branch length, support values, quotes."""
        # Remove trailing :number or )number:number
        name = name.strip().strip("'\"")
        # Remove branch length
        if ":" in name:
            parts = name.split(":")
            # Only take the part before : if it's not a numeric suffix on a label
            name = parts[0]
        return name[:40]  # truncate long names

    def _render(node_str: str, prefix: str = "", is_last: bool = True) -> list[str]:
        """Parse subtree. Returns list of rendered lines."""
        node_str = node_str.strip()
        if not node_str:
            return []

        # Strip outer parens if they wrap the entire node
        while node_str.startswith("("):
            depth = 0
            closes_at = -1
            for i, c in enumerate(node_str):
                if c == "(":
                    depth += 1
                elif c == ")":
                    depth -= 1
                    if depth == 0:
                        closes_at = i
                        break
            if closes_at == -1:
                break
            # Check if everything after ) is just metadata (support/branch length)
            suffix = node_str[closes_at + 1:]
            if suffix == "" or all(c in "0123456789.:-" for c in suffix):
                node_str = node_str[1:closes_at]
            else:
                break

        # Find top-level commas (depth 0)
        depth = 0
        splits = []
        start = 0
        for i, c in enumerate(node_str):
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
            elif c == "," and depth == 0:
                splits.append((start, i))
                start = i + 1

        if not splits:
            # Single leaf
            return [f"{prefix}{'└── ' if is_last else '├── '}{_clean(node_str)}"]

        splits.append((start, len(node_str)))
        children = [node_str[s:e] for s, e in splits]

        # Render: last child first → top of display tree
        lines = []
        for idx, child in enumerate(reversed(children)):
            child_is_last = (idx == 0)
            connector = "    " if is_last else "│   "
            child_lines = _render(child, prefix + connector, child_is_last)
            lines = child_lines + lines

        return lines

    try:
        lines = _render(newick, "", True)
    except Exception as e:
        return f"(Parse error: {e})\n{newick[:200]}"

    return "\n".join(lines)


def _ggtree_script(tree_path: str, out_path: str, title: str = "") -> str:
    """Generate an R script for ggtree rendering."""
    return f"""
library(ggtree)
library(ggplot2)

tree <- read.tree("{tree_path}")
p <- ggtree(tree) +
     geom_tiplab(size=3, align=TRUE) +
     labs(title="{title}") +
     theme_tree2()

ggsave("{out_path}", p, width=10, height=8, dpi=300)
cat("Saved:", "{out_path}")
"""


class VisualizationPlugin(Plugin):
    name = "visualization"
    version = "0.1.0"
    description = "Tree visualization — ASCII preview + ggtree publication figures"

    def run(self, input_data, config=None) -> PluginResult:
        cfg = config or {}
        mode = cfg.get("mode", "ascii")  # ascii, ggtree
        title = cfg.get("title", "Phylogenetic Tree")
        out_file = cfg.get("output", "")

        # Resolve input
        if isinstance(input_data, str) and Path(input_data).exists():
            tree_text = Path(input_data).read_text(encoding="utf-8").strip()
        else:
            tree_text = str(input_data).strip()

        if not tree_text.startswith("("):
            return PluginResult(ok=False, errors=["Input does not look like a newick tree"])

        if mode == "ggtree":
            rscript = _find_rscript()
            if not rscript:
                return PluginResult(
                    ok=False,
                    errors=["R/Rscript not found. Install R from https://cran.r-project.org"],
                )

            # Write temp R script
            with tempfile.NamedTemporaryFile(mode="w", suffix=".R", delete=False) as f:
                # First write tree to temp file
                tree_tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".nwk", delete=False)
                tree_tmp.write(tree_text)
                tree_tmp.close()

                out = out_file or tempfile.mktemp(suffix=".png")
                script = _ggtree_script(tree_tmp.name, out, title)
                f.write(script)
                f.close()

                result = subprocess.run(
                    [rscript, "--no-save", f.name],
                    capture_output=True, text=True, timeout=120,
                )
                Path(f.name).unlink(missing_ok=True)
                Path(tree_tmp.name).unlink(missing_ok=True)

                if result.returncode != 0:
                    return PluginResult(
                        ok=False,
                        errors=[f"ggtree failed: {result.stderr[:500]}"],
                    )

                return PluginResult(
                    ok=True,
                    data={"output_image": out, "stdout": result.stdout},
                )

        # Default: ASCII preview
        ascii_art = _ascii_tree(tree_text)
        return PluginResult(
            ok=True,
            data={"ascii_tree": ascii_art},
            warnings=["ASCII preview only. Install R + ggtree for publication figures."],
        )

    def validate(self) -> PluginResult:
        return PluginResult(ok=True)
