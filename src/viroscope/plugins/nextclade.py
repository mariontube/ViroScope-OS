"""Nextclade QC plugin — clade assignment, mutation calling, sequence QC."""

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from ..core.plugin import Plugin, PluginResult

# ponytail: known datasets, add more as needed
KNOWN_DATASETS = {
    "flu_h3n2_ha": {
        "shortcut": "flu_h3n2_ha",
        "description": "Influenza A H3N2 HA (A/Darwin/6/2021)",
    },
    "flu_h1n1pdm_ha": {
        "shortcut": "flu_h1n1pdm_ha",
        "description": "Influenza A H1N1pdm HA (A/Wisconsin/588/2019)",
    },
    "flu_h5_ha": {
        "shortcut": "flu_h5n1_ha",
        "description": "Influenza A H5 HA",
    },
}

# Where datasets are cached
DATA_DIR = Path.home() / ".viroscope" / "nextclade_data"


def _find_nextclade() -> str | None:
    """Find nextclade binary in PATH or known locations."""
    for name in ["nextclade", "nextclade.exe"]:
        path = shutil.which(name)
        if path:
            return path
    # Check home bin
    for name in ["nextclade.exe", "nextclade"]:
        candidate = Path.home() / "bin" / name
        if candidate.exists():
            return str(candidate)
    return None


def _ensure_dataset(dataset_name: str) -> tuple[str | None, str | None]:
    """Download dataset if not cached. Returns (dataset_path, error)."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    dataset_dir = DATA_DIR / dataset_name

    if dataset_dir.exists() and (dataset_dir / "virus_properties.json").exists():
        return str(dataset_dir), None

    # Try to download
    nextclade = _find_nextclade()
    if not nextclade:
        return None, "Nextclade not found. Install: see https://clades.nextstrain.org"

    result = subprocess.run(
        [nextclade, "dataset", "get", "--name", dataset_name, "--output-dir", str(dataset_dir)],
        capture_output=True, text=True, timeout=300,
    )
    if result.returncode != 0:
        return None, f"Dataset download failed: {result.stderr[:200]}"

    return str(dataset_dir), None


class NextcladePlugin(Plugin):
    name = "nextclade"
    version = "0.1.0"
    description = "Nextclade QC: clade assignment, mutation calling, alignment quality"

    def run(self, input_data, config=None) -> PluginResult:
        cfg = config or {}
        dataset = cfg.get("dataset", "flu_h3n2_ha")

        # Find input
        if isinstance(input_data, str) and Path(input_data).exists():
            fasta_path = Path(input_data)
        else:
            # Write temp file
            tmp = tempfile.NamedTemporaryFile(
                mode="w", suffix=".fasta", delete=False, encoding="utf-8"
            )
            tmp.write(str(input_data))
            tmp.close()
            fasta_path = Path(tmp.name)

        # Find nextclade
        nextclade = _find_nextclade()
        if not nextclade:
            return PluginResult(
                ok=False,
                errors=["Nextclade not installed. Download from https://clades.nextstrain.org"],
            )

        # Ensure dataset
        dataset_path, err = _ensure_dataset(dataset)
        if err:
            return PluginResult(ok=False, errors=[err])

        # Run nextclade
        out_dir = tempfile.mkdtemp(prefix="nextclade_")
        result = subprocess.run(
            [
                nextclade, "run",
                "--input-dataset", dataset_path,
                "--output-all", out_dir,
                str(fasta_path),
            ],
            capture_output=True, text=True, timeout=600,
        )

        if result.returncode != 0:
            return PluginResult(
                ok=False,
                errors=[f"Nextclade failed (exit {result.returncode}): {result.stderr[:500]}"],
            )

        # Parse results
        report = self._parse_output(out_dir)

        # Cleanup temp
        if fasta_path != Path(input_data):
            Path(fasta_path).unlink(missing_ok=True)

        return PluginResult(
            ok=True,
            data={
                "report": report,
                "output_dir": out_dir,
            },
            warnings=report.get("_warnings", []),
        )

    def _parse_output(self, out_dir: str) -> dict:
        """Parse nextclade TSV output into structured report."""
        out = Path(out_dir)
        tsv_file = out / "nextclade.tsv"
        json_file = out / "nextclade.json"

        if not tsv_file.exists():
            return {"error": "No output found", "_warnings": []}

        lines = tsv_file.read_text(encoding="utf-8").strip().split("\n")
        if len(lines) < 2:
            return {"error": "Empty output", "_warnings": []}

        headers = lines[0].split("\t")
        rows = [dict(zip(headers, l.split("\t"))) for l in lines[1:]]

        total = len(rows)
        warnings = []

        # Count quality flags
        qc_overall = sum(1 for r in rows if r.get("qc.overallStatus") == "bad")
        qc_mixed = sum(1 for r in rows if r.get("qc.overallStatus") == "mediocre" or r.get("qc.overallStatus") == "warn")
        qc_good = total - qc_overall - qc_mixed if "qc.overallStatus" in headers else total

        # Clade distribution
        clades = {}
        for r in rows:
            c = r.get("clade", "unknown")
            clades[c] = clades.get(c, 0) + 1

        # Mutations
        total_private_mutations = sum(
            int(r.get("qc.privateMutations.total", 0))
            for r in rows
            if r.get("qc.privateMutations.total", "").isdigit()
        )

        # Missing data
        missing_sites = sum(
            int(r.get("qc.missingData.totalMissing", 0))
            for r in rows
            if r.get("qc.missingData.totalMissing", "").isdigit()
        )

        # Warnings
        if qc_overall > 0:
            warnings.append(f"{qc_overall}/{total} sequences failed QC")
        if qc_mixed > 0:
            warnings.append(f"{qc_mixed}/{total} sequences have mediocre QC")
        if total_private_mutations > total * 5:
            warnings.append(f"High private mutation count ({total_private_mutations}) — check for contamination")

        return {
            "dataset": tsv_file.stem,
            "total_sequences": total,
            "qc_good": qc_good,
            "qc_bad": qc_overall,
            "qc_mediocre": qc_mixed,
            "clade_distribution": clades,
            "total_private_mutations": total_private_mutations,
            "total_missing_sites": missing_sites,
            "per_sequence": [
                {
                    "seqName": r.get("seqName", ""),
                    "clade": r.get("clade", ""),
                    "qc_status": r.get("qc.overallStatus", ""),
                    "private_mutations": r.get("qc.privateMutations.total", ""),
                    "missing_sites": r.get("qc.missingData.totalMissing", ""),
                    "total_substitutions": r.get("totalSubstitutions", ""),
                    "total_deletions": r.get("totalDeletions", ""),
                }
                for r in rows
            ],
            "_warnings": warnings,
        }

    def validate(self) -> PluginResult:
        if not _find_nextclade():
            return PluginResult(
                ok=False,
                errors=["Nextclade not found. Install: https://clades.nextstrain.org"],
            )
        return PluginResult(ok=True)
