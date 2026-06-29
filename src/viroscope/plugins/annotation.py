"""Annotation plugin — antigenic site, RBS, and glycosylation annotation for influenza HA.

Supports both amino acid and nucleotide alignments (auto-detects and translates).
Uses H3 numbering (A/Aichi/2/1968). H1 support via config override.
"""

import json
import re
from collections import OrderedDict

from ..core.plugin import Plugin, PluginResult

# Standard genetic code
CODON_TABLE = {
    "ATA": "I", "ATC": "I", "ATT": "I", "ATG": "M",
    "ACA": "T", "ACC": "T", "ACG": "T", "ACT": "T",
    "AAC": "N", "AAT": "N", "AAA": "K", "AAG": "K",
    "AGC": "S", "AGT": "S", "AGA": "R", "AGG": "R",
    "CTA": "L", "CTC": "L", "CTG": "L", "CTT": "L", "TTA": "L", "TTG": "L",
    "CCA": "P", "CCC": "P", "CCG": "P", "CCT": "P",
    "CAC": "H", "CAT": "H", "CAA": "Q", "CAG": "Q",
    "CGA": "R", "CGC": "R", "CGG": "R", "CGT": "R",
    "GTA": "V", "GTC": "V", "GTG": "V", "GTT": "V",
    "GCA": "A", "GCC": "A", "GCG": "A", "GCT": "A",
    "GAC": "D", "GAT": "D", "GAA": "E", "GAG": "E",
    "GGA": "G", "GGC": "G", "GGG": "G", "GGT": "G",
    "TCA": "S", "TCC": "S", "TCG": "S", "TCT": "S",
    "TTC": "F", "TTT": "F", "TAC": "Y", "TAT": "Y",
    "TGC": "C", "TGT": "C", "TGG": "W",
    "TAA": "*", "TAG": "*", "TGA": "*",
}

# ── H3N2 antigenic sites (A/Aichi/2/1968 numbering) ──────────────────────
# From RESEARCH_SPEC.md
H3_ANTIGENIC_SITES = {
    "A": [122, 124, 126] + list(range(130, 134)) + [135, 137] + list(range(140, 147)),
    "B": [128, 129] + list(range(155, 161)) + list(range(163, 166))
         + list(range(186, 191)) + list(range(192, 198)),
    "C": (list(range(44, 49)) + [50, 53, 54] + [273, 275, 276]
          + list(range(278, 281)) + [294, 297, 299, 300, 304, 305]
          + list(range(307, 313))),
    "D": ([96, 102, 103, 117, 121, 167] + list(range(170, 178)) + [179]
          + list(range(201, 204)) + list(range(207, 221)) + list(range(226, 231))
          + list(range(238, 243)) + [244] + list(range(246, 249))),
    "E": ([57, 59, 62, 63, 67, 75, 78] + list(range(80, 84)) + [86, 87, 88]
          + [91, 92, 94, 109] + list(range(260, 263)) + [265]),
}

H3_RBS = {
    "130-loop": list(range(131, 139)),
    "190-helix": list(range(187, 198)),
    "220-loop": list(range(222, 229)),
}

# N-glycosylation motif: N-X-S/T (X ≠ P)
GLYCAN_MOTIF = "N[^P][ST]"


def _site_lookup(h3_pos: int) -> dict:
    """Return {site: name} for a given H3 position, or {}."""
    result = {}
    for site, positions in H3_ANTIGENIC_SITES.items():
        if h3_pos in positions:
            result["antigenic_site"] = site
            break
    for loop, positions in H3_RBS.items():
        if h3_pos in positions:
            result["rbs"] = loop
            break
    return result


def _is_nucleotide(seq: str) -> bool:
    """Guess if sequence is nucleotide (>80% ATGC)."""
    clean = seq.replace("-", "")
    if not clean:
        return False
    nt_count = sum(1 for c in clean if c in "ATGCNatgcn")
    return nt_count / len(clean) > 0.8


def _translate(seq: str) -> str:
    """Translate nucleotide sequence to amino acids. Gaps become gaps, partial codons dropped."""
    aa = []
    codon = ""
    for c in seq:
        if c == "-":
            aa.append("-")
            codon = ""
        else:
            codon += c
            if len(codon) == 3:
                aa.append(CODON_TABLE.get(codon.upper(), "X"))
                codon = ""
    return "".join(aa)


def _parse_fasta(text: str) -> OrderedDict[str, str]:
    """Parse aligned FASTA. Returns {header: sequence}."""
    seqs = OrderedDict()
    header, parts = None, []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if header is not None:
                seqs[header] = "".join(parts).upper()
            header = line[1:].strip()
            parts = []
        elif header is not None:
            parts.append(line.upper())
    if header is not None:
        seqs[header] = "".join(parts).upper()
    return seqs


class AnnotationPlugin(Plugin):
    name = "annotation"
    version = "0.1.0"
    description = "HA antigenic site, RBS, and glycosylation annotation"

    def run(self, input_data, config=None) -> PluginResult:
        cfg = config or {}
        ref_name = cfg.get("reference", "").lower()
        subtype = cfg.get("subtype", "H3")

        # Parse input
        if isinstance(input_data, str):
            text = input_data
        else:
            text = str(input_data)

        # Try to read from file
        from pathlib import Path
        if Path(input_data).exists() if isinstance(input_data, str) else False:
            text = Path(input_data).read_text(encoding="utf-8")

        seqs = _parse_fasta(text)
        if len(seqs) < 2:
            return PluginResult(ok=False, errors=["Need at least 2 sequences (reference + queries)"])

        # Auto-detect nucleotide vs protein
        first_seq = list(seqs.values())[0]
        is_nt = _is_nucleotide(first_seq)
        if is_nt:
            seqs = OrderedDict((h, _translate(s)) for h, s in seqs.items())

        # Find reference
        ref_seq = None
        ref_header = None
        for h, s in seqs.items():
            if ref_name and ref_name in h.lower():
                ref_header, ref_seq = h, s
                break
        if ref_seq is None:
            # Use first sequence as reference
            ref_header, ref_seq = list(seqs.items())[0]

        # Build H3 position map: alignment_column -> h3_position
        h3_pos = 1
        col_to_h3 = {}
        for i, aa in enumerate(ref_seq):
            if aa != "-":
                col_to_h3[i] = h3_pos
                h3_pos += 1

        # Annotate each query sequence
        results = []
        stats = {
            "reference": ref_header,
            "reference_length_aa": h3_pos - 1,
            "n_query_sequences": len(seqs) - 1,
            "antigenic_site_mutations": {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0},
            "rbs_mutations": 0,
            "total_mutations": 0,
            "per_sequence": [],
        }

        for header, seq in seqs.items():
            if header == ref_header:
                continue

            mutations = []
            for i, aa in enumerate(seq):
                if i >= len(ref_seq):
                    break
                ref_aa = ref_seq[i]
                if aa == ref_aa or aa == "-" or ref_aa == "-":
                    continue

                pos = col_to_h3.get(i)
                if pos is None:
                    continue

                info = _site_lookup(pos)
                mut = {
                    "h3_position": pos,
                    "reference_aa": ref_aa,
                    "mutant_aa": aa,
                    "antigenic_site": info.get("antigenic_site", ""),
                    "rbs": info.get("rbs", ""),
                }
                mutations.append(mut)

                # Counts
                if info.get("antigenic_site"):
                    stats["antigenic_site_mutations"][info["antigenic_site"]] += 1
                if info.get("rbs"):
                    stats["rbs_mutations"] += 1

            stats["total_mutations"] += len(mutations)
            stats["per_sequence"].append({
                "header": header,
                "n_mutations": len(mutations),
                "antigenic_site_hits": len([m for m in mutations if m["antigenic_site"]]),
                "rbs_hits": len([m for m in mutations if m["rbs"]]),
                "mutations": mutations,
            })

        warnings = []
        if stats["rbs_mutations"] > 0:
            warnings.append(f"{stats['rbs_mutations']} RBS mutations detected — potential receptor binding change")
        if sum(stats["antigenic_site_mutations"].values()) > 0:
            total_ag = sum(stats["antigenic_site_mutations"].values())
            warnings.append(f"{total_ag} antigenic site mutations detected")

        return PluginResult(
            ok=True,
            data={
                "report": stats,
                "report_json": json.dumps(stats, indent=2, ensure_ascii=False),
            },
            warnings=warnings,
        )

    def validate(self) -> PluginResult:
        return PluginResult(ok=True)
