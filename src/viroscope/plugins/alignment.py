"""Alignment plugin — MAFFT wrapper for multiple sequence alignment."""

import shutil
import subprocess
import tempfile
from pathlib import Path

from ..core.plugin import Plugin, PluginResult

# ponytail: look for mafft in common locations
_MAFFT_PATHS = [
    Path.home() / "bin" / "mafft" / "mafft.bat",
    Path.home() / "bin" / "mafft.bat",
]


def _find_mafft() -> str | None:
    """Find MAFFT executable."""
    for p in _MAFFT_PATHS:
        if p.exists():
            return str(p)
    if shutil.which("mafft"):
        return "mafft"
    if shutil.which("mafft.bat"):
        return "mafft.bat"
    return None


class AlignmentPlugin(Plugin):
    name = "alignment"
    version = "0.1.0"
    description = "Multiple sequence alignment with MAFFT"

    def run(self, input_data, config=None) -> PluginResult:
        cfg = config or {}
        method = cfg.get("method", "auto")
        nthread = cfg.get("nthread", "2")

        mafft = _find_mafft()
        if not mafft:
            return PluginResult(
                ok=False,
                errors=["MAFFT not found. Install from https://mafft.cbrc.jp/alignment/software/"],
            )

        # Resolve input
        if isinstance(input_data, str) and Path(input_data).exists():
            fasta_path = Path(input_data)
            tmp_input = None
        else:
            tmp_input = tempfile.NamedTemporaryFile(
                mode="w", suffix=".fasta", delete=False, encoding="utf-8"
            )
            tmp_input.write(str(input_data))
            tmp_input.close()
            fasta_path = Path(tmp_input.name)

        # Build MAFFT command
        cmd = [mafft]
        if method == "auto":
            cmd.append("--auto")
        elif method == "linsi":
            cmd.extend(["--localpair", "--maxiterate", "1000"])
        elif method == "ginsi":
            cmd.extend(["--globalpair", "--maxiterate", "1000"])
        elif method == "fftns":
            cmd.append("--retree")
            cmd.append("1")
        cmd.extend(["--thread", str(nthread)])
        cmd.append(str(fasta_path))

        # Run
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            return PluginResult(
                ok=False,
                errors=[f"MAFFT failed (exit {result.returncode}): {result.stderr[:500]}"],
            )

        aligned = result.stdout
        if not aligned.startswith(">"):
            return PluginResult(
                ok=False,
                errors=["MAFFT produced no valid alignment output"],
            )

        # Compute stats
        stats = _compute_stats(aligned)

        # Cleanup
        if tmp_input:
            Path(tmp_input.name).unlink(missing_ok=True)

        return PluginResult(
            ok=True,
            data={
                "aligned_fasta": aligned,
                "stats": stats,
            },
            warnings=stats.get("_warnings", []),
        )

    def validate(self) -> PluginResult:
        if not _find_mafft():
            return PluginResult(
                ok=False,
                errors=["MAFFT not found. Install: https://mafft.cbrc.jp/alignment/software/"],
            )
        return PluginResult(ok=True)


def _compute_stats(fasta_text: str) -> dict:
    """Compute alignment statistics."""
    warnings = []
    seqs = {}
    header = None
    for line in fasta_text.split("\n"):
        line = line.strip()
        if line.startswith(">"):
            header = line[1:].strip()
            seqs[header] = ""
        elif header is not None:
            seqs[header] += line

    if not seqs:
        return {"error": "No sequences", "_warnings": []}

    lengths = {h: len(s) for h, s in seqs.items()}
    align_len = max(lengths.values())
    gaps = {h: s.count("-") for h, s in seqs.items()}
    total_gaps = sum(gaps.values())

    # Gap percentage per sequence
    gap_pct = {h: round(gaps[h] / align_len * 100, 1) for h in gaps}

    high_gap = [h for h, p in gap_pct.items() if p > 50]
    if high_gap:
        warnings.append(f"{len(high_gap)} sequences with >50% gaps")

    # Consensus
    consensus = ""
    for i in range(align_len):
        col = [s[i] for s in seqs.values() if i < len(s)]
        consensus += max(set(col), key=col.count) if col else "-"

    identity = sum(1 for i in range(align_len) if all(
        (s[i] if i < len(s) else "-") == consensus[i] for s in seqs.values()
    )) / align_len * 100

    return {
        "n_sequences": len(seqs),
        "alignment_length": align_len,
        "min_length": min(lengths.values()),
        "max_length": max(lengths.values()),
        "total_gaps": total_gaps,
        "gap_percentage": round(total_gaps / (align_len * len(seqs)) * 100, 1),
        "identity_pct": round(identity, 1),
        "high_gap_sequences": high_gap,
        "_warnings": warnings,
    }
