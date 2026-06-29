"""QC plugin — sequence quality control. Deduplicate, validate, report."""

import json
from collections import Counter, OrderedDict
from pathlib import Path

from ..core.plugin import Plugin, PluginResult

# ponytail: hardcoded defaults; config file overrides these
DEFAULTS = {
    "min_length": 200,
    "max_ambiguous_pct": 50.0,  # sequences with >50% N are flagged
    "allowed_bases": set("ATGCNatgcn-"),
}


def _parse_fasta(text: str) -> tuple[OrderedDict[str, str], list[str]]:
    """Parse FASTA text. Returns (header->sequence, duplicate_header_list). Keeps first of duplicate headers."""
    seqs = OrderedDict()
    dup_headers = []
    header, parts = None, []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if header is not None:
                if header in seqs:
                    dup_headers.append(header)
                else:
                    seqs[header] = "".join(parts)
            header = line[1:].strip()
            parts = []
        elif header is not None:
            parts.append(line)
    if header is not None:
        if header in seqs:
            dup_headers.append(header)
        else:
            seqs[header] = "".join(parts)
    return seqs, dup_headers


def _format_fasta(seqs: OrderedDict[str, str]) -> str:
    """Format sequences back to FASTA text."""
    out = []
    for header, seq in seqs.items():
        out.append(f">{header}")
        # wrap at 70 chars
        for i in range(0, len(seq), 70):
            out.append(seq[i : i + 70])
    return "\n".join(out) + "\n"


class QCPlugin(Plugin):
    name = "qc"
    version = "0.2.0"
    description = "Sequence QC: deduplicate, validate, flag low-quality sequences"

    def run(self, input_data, config=None) -> PluginResult:
        cfg = {**DEFAULTS, **(config or {})}
        path = Path(input_data) if isinstance(input_data, str) else None

        if path and path.exists():
            text = path.read_text(encoding="utf-8")
            fname = str(path)
        else:
            text = str(input_data)
            fname = "<stdin>"

        seqs, dup_headers = _parse_fasta(text)

        # --- Report template ---
        report = {
            "file": fname,
            "input_count": len(seqs),
            "duplicate_headers": [],
            "duplicate_sequences": [],
            "short_sequences": [],
            "high_ambiguous": [],
            "non_standard_bases": [],
            "output_count": 0,
            "removed_total": 0,
        }

        # Add duplicate header info to report
        report["duplicate_headers"] = dup_headers

        warnings = []
        clean = OrderedDict()
        seen_seqs: dict[str, str] = {}  # seq_hash -> header (first seen)

        for header, seq in seqs.items():
            # 1. Duplicate sequence detection
            seq_hash = seq.upper()
            if seq_hash in seen_seqs:
                report["duplicate_sequences"].append(
                    {"header": header, "duplicate_of": seen_seqs[seq_hash]}
                )
                continue

            seen_seqs[seq_hash] = header

            # 2. Short sequence
            if len(seq) < cfg["min_length"]:
                report["short_sequences"].append(
                    {"header": header, "length": len(seq)}
                )
                continue

            # 3. Ambiguous base check
            non_standard = [b for b in seq if b not in cfg["allowed_bases"]]
            ambig_count = sum(1 for b in seq.upper() if b == "N")
            ambig_pct = (ambig_count / len(seq)) * 100

            if ambig_pct > cfg["max_ambiguous_pct"]:
                report["high_ambiguous"].append(
                    {"header": header, "n_count": ambig_count, "pct": round(ambig_pct, 1)}
                )

            if non_standard:
                report["non_standard_bases"].append(
                    {
                        "header": header,
                        "bases": list(set(non_standard)),
                        "count": len(non_standard),
                    }
                )

            # 4. Keep clean sequences (even with warnings — just flag, don't drop)
            clean[header] = seq

        report["output_count"] = len(clean)
        report["removed_total"] = report["input_count"] - report["output_count"]

        # Build warnings
        if dup_headers:
            warnings.append(f"{len(dup_headers)} duplicate header(s) found (keeping first occurrence)")
        if report["duplicate_sequences"]:
            warnings.append(f"{len(report['duplicate_sequences'])} duplicate sequences removed")
        if report["short_sequences"]:
            warnings.append(f"{len(report['short_sequences'])} short sequences removed (<{cfg['min_length']}bp)")
        if report["high_ambiguous"]:
            warnings.append(f"{len(report['high_ambiguous'])} sequences with >{cfg['max_ambiguous_pct']}% ambiguous bases (flagged, not removed)")
        if report["non_standard_bases"]:
            warnings.append(f"{len(report['non_standard_bases'])} sequences with non-standard bases (flagged)")

        # Output: cleaned FASTA + JSON report
        clean_fasta = _format_fasta(clean)
        report_json = json.dumps(report, indent=2, ensure_ascii=False)

        return PluginResult(
            ok=True,
            data={
                "cleaned_fasta": clean_fasta,
                "report": report,
                "report_json": report_json,
            },
            warnings=warnings,
        )

    def validate(self) -> PluginResult:
        return PluginResult(ok=True)
