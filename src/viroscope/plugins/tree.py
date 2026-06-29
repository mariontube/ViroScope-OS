"""Tree plugin — IQ-TREE wrapper for maximum likelihood phylogeny."""

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from ..core.plugin import Plugin, PluginResult


def _find_iqtree() -> str | None:
    """Find IQ-TREE binary."""
    for name in ["iqtree3.exe", "iqtree3", "iqtree.exe", "iqtree"]:
        p = shutil.which(name)
        if p:
            return p
    for name in ["iqtree3.exe", "iqtree.exe", "iqtree3", "iqtree"]:
        c = Path.home() / "bin" / name
        if c.exists():
            return str(c)
    return None


class TreePlugin(Plugin):
    name = "tree"
    version = "0.1.0"
    description = "ML phylogeny with IQ-TREE — ModelFinder + ultrafast bootstrap"

    def run(self, input_data, config=None) -> PluginResult:
        cfg = config or {}
        method = cfg.get("method", "auto")       # auto, fast, fixed
        bootstrap = int(cfg.get("bootstrap", 1000))
        nthread = cfg.get("nthread", "AUTO")

        iqtree = _find_iqtree()
        if not iqtree:
            return PluginResult(
                ok=False,
                errors=["IQ-TREE not found. Download from http://www.iqtree.org"],
            )

        # Resolve input (must be aligned FASTA)
        if isinstance(input_data, str) and Path(input_data).exists():
            fasta_path = Path(input_data).resolve()
            tmp_input = None
        else:
            tmp_input = tempfile.NamedTemporaryFile(
                mode="w", suffix=".fasta", delete=False, encoding="utf-8"
            )
            tmp_input.write(str(input_data))
            tmp_input.close()
            fasta_path = Path(tmp_input.name).resolve()

        # Temp output directory
        out_dir = Path(tempfile.mkdtemp(prefix="iqtree_"))
        prefix = out_dir / "viroscope_tree"

        # Build command
        cmd = [iqtree, "-s", str(fasta_path), "--prefix", str(prefix)]

        if method == "fast":
            cmd.extend(["-m", "GTR+F+I+G4", "-fast"])
        elif method == "fixed":
            model = cfg.get("model", "GTR+F+I+G4")
            cmd.extend(["-m", model])
        else:
            # auto: ModelFinder
            cmd.extend(["-m", "MFP"])

        if bootstrap > 0:
            cmd.extend(["-B", str(bootstrap)])

        cmd.extend(["-T", str(nthread)])

        # Run
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        if result.returncode != 0:
            return PluginResult(
                ok=False,
                errors=[f"IQ-TREE failed (exit {result.returncode}): {result.stderr[:500]}"],
            )

        # Parse outputs
        treefile = prefix.with_suffix(".treefile")
        logfile = prefix.with_suffix(".iqtree")
        contree = prefix.with_suffix(".contree")

        if not treefile.exists():
            return PluginResult(ok=False, errors=["No .treefile produced"])

        tree_text = treefile.read_text(encoding="utf-8").strip()
        log_text = logfile.read_text(encoding="utf-8") if logfile.exists() else ""

        stats = _parse_iqtree_log(log_text)
        stats["output_tree"] = treefile.name
        stats["output_prefix"] = str(prefix)

        warnings = []
        if stats.get("bootstrap_support", 0) < 70:
            warnings.append("Average bootstrap support < 70% — treat topology with caution")

        # Cleanup temp input
        if tmp_input:
            Path(tmp_input.name).unlink(missing_ok=True)

        return PluginResult(
            ok=True,
            data={
                "tree_newick": tree_text,
                "stats": stats,
                "output_dir": str(out_dir),
            },
            warnings=warnings,
        )

    def validate(self) -> PluginResult:
        if not _find_iqtree():
            return PluginResult(
                ok=False,
                errors=["IQ-TREE not found. Download from http://www.iqtree.org"],
            )
        return PluginResult(ok=True)


def _parse_iqtree_log(text: str) -> dict:
    """Extract key statistics from IQ-TREE .iqtree log."""
    stats: dict = {}

    # Model
    m = re.search(r"Best-fit model according to BIC:\s*(\S+)", text)
    if m:
        stats["best_model"] = m.group(1)

    # Log-likelihood
    m = re.search(r"Log-likelihood of the tree:\s*(-?[\d.]+)", text)
    if m:
        stats["log_likelihood"] = float(m.group(1))

    # Tree length
    m = re.search(r"(?:Total )?(?:T|t)ree length[:\s]*([\d.]+)", text)
    if m:
        stats["tree_length"] = float(m.group(1))

    # Number of parsimony-informative sites
    m = re.search(r"parsimony-informative:\s*(\d+)", text)
    if m:
        stats["parsimony_informative"] = int(m.group(1))

    # Constant sites
    m = re.search(r"constant sites:\s*(\d+)", text)
    if m:
        stats["constant_sites"] = int(m.group(1))

    # Number of sequences
    m = re.search(r"sequences:\s*(\d+)", text)
    if m:
        stats["n_sequences"] = int(m.group(1))

    # Alignment length
    m = re.search(r"alignment has\s*(\d+)\s*sites", text)
    if m:
        stats["alignment_length"] = int(m.group(1))

    # Average bootstrap support (from consensus tree or log)
    avg_bs = _avg_bootstrap(text)
    if avg_bs is not None:
        stats["bootstrap_support"] = round(avg_bs, 1)

    return stats


def _avg_bootstrap(text: str) -> float | None:
    """Extract average bootstrap support from UFboot output."""
    vals = []
    for m in re.finditer(r"\)(\d+)[/:]", text):
        vals.append(int(m.group(1)))
    if not vals:
        return None
    return sum(vals) / len(vals)
