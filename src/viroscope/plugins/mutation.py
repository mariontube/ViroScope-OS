"""Mutation plugin — mutation tracking, frequency matrix, and antigenic drift scoring.

Pure Python, no external tools.
"""
import json
from collections import OrderedDict, Counter

from ..core.plugin import Plugin, PluginResult

# Same site definitions as annotation plugin
H3_ANTIGENIC_SITES = {
    "A": [122, 124, 126] + list(range(130, 134)) + [135, 137] + list(range(140, 147)),
    "B": [128, 129] + list(range(155, 161)) + list(range(163, 166)) + list(range(186, 191)) + list(range(192, 198)),
    "C": (list(range(44, 49)) + [50, 53, 54] + [273, 275, 276] + list(range(278, 281))
          + [294, 297, 299, 300, 304, 305] + list(range(307, 313))),
    "D": ([96, 102, 103, 117, 121, 167] + list(range(170, 178)) + [179] + list(range(201, 204))
          + list(range(207, 221)) + list(range(226, 231)) + list(range(238, 243))
          + [244] + list(range(246, 249))),
    "E": ([57, 59, 62, 63, 67, 75, 78] + list(range(80, 84)) + [86, 87, 88]
          + [91, 92, 94, 109] + list(range(260, 263)) + [265]),
}

CODON_TABLE = {
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


def _translate(seq: str) -> str:
    aa, codon = [], ""
    for c in seq:
        if c == "-": aa.append("-"); codon = ""
        else:
            codon += c
            if len(codon) == 3: aa.append(CODON_TABLE.get(codon.upper(), "X")); codon = ""
    return "".join(aa)


def _is_nt(seq: str) -> bool:
    clean = seq.replace("-", "")
    return sum(1 for c in clean if c in "ATGCN") / max(len(clean), 1) > 0.8


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


class MutationPlugin(Plugin):
    name = "mutation"
    version = "0.1.0"
    description = "Mutation tracking: frequency matrix, antigenic drift scoring"

    def run(self, input_data, config=None) -> PluginResult:
        from pathlib import Path
        if isinstance(input_data, str) and Path(input_data).exists():
            text = Path(input_data).read_text(encoding="utf-8")
        else:
            text = str(input_data)

        seqs = _parse_fasta(text)
        if len(seqs) < 2:
            return PluginResult(ok=False, errors=["Need >= 2 sequences"])

        # Auto-translate if nucleotide
        first = list(seqs.values())[0]
        if _is_nt(first):
            seqs = OrderedDict((h, _translate(s)) for h, s in seqs.items())

        headers = list(seqs.keys())
        ref_h, ref_s = headers[0], seqs[headers[0]]
        queries = [(h, seqs[h]) for h in headers[1:]]

        # Map alignment column → H3 position (using reference)
        h3 = 1
        col_h3 = {}
        for i, aa in enumerate(ref_s):
            if aa != "-":
                col_h3[i] = h3
                h3 += 1

        # Build mutation matrix
        mutations = []      # flat list
        by_position = {}    # h3_pos → {header: {ref, mut, site}}
        ant_counts = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0}

        for q_h, q_s in queries:
            for i, aa in enumerate(q_s):
                if i >= len(ref_s): break
                r = ref_s[i]
                if aa == r or aa == "-" or r == "-": continue
                pos = col_h3.get(i)
                if pos is None: continue

                # Find antigenic site
                site = ""
                for sname, positions in H3_ANTIGENIC_SITES.items():
                    if pos in positions:
                        site = sname
                        ant_counts[sname] += 1
                        break

                mut = {"header": q_h, "h3_position": pos, "ref_aa": r, "mut_aa": aa, "antigenic_site": site}
                mutations.append(mut)

                if pos not in by_position:
                    by_position[pos] = {}
                by_position[pos][q_h] = {"ref": r, "mut": aa, "site": site}

        # Antigenic drift score: weighted sum of antigenic site mutations
        weights = {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1}
        drift_scores = {}
        for q_h, _ in queries:
            score = sum(weights.get(m["antigenic_site"], 0) for m in mutations if m["header"] == q_h)
            drift_scores[q_h] = score

        # Heatmap data: rows=positions, cols=strains
        heatmap = []
        for pos in sorted(by_position):
            row = {"h3_position": pos}
            for strain_hits in by_position[pos].values():
                row["antigenic_site"] = strain_hits.get("site", "")
                break
            for h in headers[1:]:
                if h in by_position[pos]:
                    row[h] = f"{by_position[pos][h]['ref']}>{by_position[pos][h]['mut']}"
                else:
                    row[h] = "."
            heatmap.append(row)

        report = {
            "n_sequences": len(seqs),
            "n_mutations": len(mutations),
            "antigenic_site_counts": ant_counts,
            "drift_scores": drift_scores,
            "heatmap": heatmap,
            "per_sequence": [
                {
                    "header": q_h,
                    "n_mutations": sum(1 for m in mutations if m["header"] == q_h),
                    "drift_score": drift_scores.get(q_h, 0),
                }
                for q_h, _ in queries
            ],
        }

        warnings = []
        total_ant = sum(ant_counts.values())
        if total_ant > 0:
            top = max(ant_counts, key=ant_counts.get)
            warnings.append(f"{total_ant} antigenic site mutations, most in site {top} ({ant_counts[top]})")

        return PluginResult(
            ok=True,
            data={"report": report, "report_json": json.dumps(report, indent=2, ensure_ascii=False)},
            warnings=warnings,
        )

    def validate(self): pass

    validate = lambda self: PluginResult(ok=True)
