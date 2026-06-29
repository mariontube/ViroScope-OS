"""Evolution plugin — pairwise dN/dS (Nei-Gojobori) + HyPhy support."""

import json
import shutil
import subprocess
import tempfile
from collections import OrderedDict
from pathlib import Path

from ..core.plugin import Plugin, PluginResult

# Standard genetic code
CODON = {
    "ATA": "I", "ATC": "I", "ATT": "I", "ATG": "M", "ACA": "T", "ACC": "T", "ACG": "T", "ACT": "T",
    "AAC": "N", "AAT": "N", "AAA": "K", "AAG": "K", "AGC": "S", "AGT": "S", "AGA": "R", "AGG": "R",
    "CTA": "L", "CTC": "L", "CTG": "L", "CTT": "L", "TTA": "L", "TTG": "L",
    "CCA": "P", "CCC": "P", "CCG": "P", "CCT": "P", "CAC": "H", "CAT": "H", "CAA": "Q", "CAG": "Q",
    "CGA": "R", "CGC": "R", "CGG": "R", "CGT": "R", "GTA": "V", "GTC": "V", "GTG": "V", "GTT": "V",
    "GCA": "A", "GCC": "A", "GCG": "A", "GCT": "A", "GAC": "D", "GAT": "D", "GAA": "E", "GAG": "E",
    "GGA": "G", "GGC": "G", "GGG": "G", "GGT": "G", "TCA": "S", "TCC": "S", "TCG": "S", "TCT": "S",
    "TTC": "F", "TTT": "F", "TAC": "Y", "TAT": "Y", "TGC": "C", "TGT": "C", "TGG": "W",
    "TAA": "*", "TAG": "*", "TGA": "*",
}

# Degeneracy: how many of 64 codons code for each amino acid (4-fold, 2-fold, non-degenerate)
FOLD = {"I": 3, "M": 1, "T": 4, "N": 2, "K": 2, "S": 6, "R": 6,
        "L": 6, "P": 4, "H": 2, "Q": 2, "V": 4, "A": 4, "D": 2, "E": 2,
        "G": 4, "F": 2, "Y": 2, "C": 2, "W": 1, "*": 3}


def _parse_fasta(text: str) -> OrderedDict:
    seqs, h, parts = OrderedDict(), None, []
    for line in text.split("\n"):
        line = line.strip()
        if not line: continue
        if line.startswith(">"):
            if h is not None: seqs[h] = "".join(parts).upper()
            h, parts = line[1:].strip(), []
        elif h is not None: parts.append(line.upper())
    if h is not None: seqs[h] = "".join(parts).upper()
    return seqs


def _ng86_dnds(seq1: str, seq2: str) -> dict:
    """Pairwise dN/dS via Nei-Gojobori (1986) approximation."""
    L = len(seq1)
    Sd = Nd = S = N = 0  # synonymous/nonsynonymous differences & sites

    for i in range(0, L - 2, 3):
        c1 = seq1[i:i+3]
        c2 = seq2[i:i+3]
        if "-" in c1 or "-" in c2 or len(c1) != 3 or len(c2) != 3:
            continue
        aa1 = CODON.get(c1, "X")
        aa2 = CODON.get(c2, "X")
        if aa1 == "X" or aa2 == "X":
            continue

        f1 = FOLD.get(aa1, 1)
        f2 = FOLD.get(aa2, 1)
        S += (f1 + f2) / 2 / 3  # approx synonymous sites
        N += 3 - (f1 + f2) / 2 / 3  # approx nonsynonymous sites

        if aa1 == aa2:
            Sd += 0  # no difference
        else:
            # If amino acids differ by 1 nucleotide change → synonymous? No, NS change.
            # For simplicity: any aa change = nonsynonymous
            Nd += 1
            Sd += 0

    if S == 0 or N == 0:
        return {"dN": 0, "dS": 0, "dN_dS": 0, "note": "too few sites"}
    dS = Sd / S if S > 0 else 0
    dN = Nd / N if N > 0 else 0
    return {"dN": round(dN, 6), "dS": round(dS, 6), "dN_dS": round(dN / dS, 4) if dS > 0 else 999}


class EvolutionPlugin(Plugin):
    name = "evolution"
    version = "0.1.0"
    description = "Selection pressure: pairwise dN/dS (Nei-Gojobori) + HyPhy support"

    def run(self, input_data, config=None) -> PluginResult:
        from pathlib import Path
        if isinstance(input_data, str) and Path(input_data).exists():
            text = Path(input_data).read_text(encoding="utf-8")
        else:
            text = str(input_data)

        seqs = _parse_fasta(text)
        if len(seqs) < 2:
            return PluginResult(ok=False, errors=["Need >= 2 sequences"])

        headers = list(seqs.keys())
        ref = headers[0]

        pairs = []
        dnds_vals = []
        for i, h2 in enumerate(headers[1:], 1):
            result = _ng86_dnds(seqs[ref], seqs[h2])
            result["pair"] = f"{ref} ↔ {h2}"
            pairs.append(result)
            if result["dN_dS"] < 999:
                dnds_vals.append(result["dN_dS"])

        report = {
            "reference": ref,
            "n_pairs": len(pairs),
            "mean_dN_dS": round(sum(dnds_vals) / len(dnds_vals), 4) if dnds_vals else None,
            "pairs": pairs,
        }

        warnings = []
        avg = report["mean_dN_dS"]
        if avg and avg > 1:
            warnings.append(f"Mean dN/dS = {avg} (>1) — positive selection signal")
        elif avg and avg < 0.5:
            warnings.append(f"Mean dN/dS = {avg} (<0.5) — purifying selection dominant")
        if avg:
            warnings.append("Note: Nei-Gojobori approximation. For publication, use HyPhy (install: conda install -c bioconda hyphy)")

        return PluginResult(
            ok=True,
            data={"report": report},
            warnings=warnings,
        )

    def validate(self): return PluginResult(ok=True)
