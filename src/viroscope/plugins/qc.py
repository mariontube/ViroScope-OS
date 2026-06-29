"""QC plugin — sequence quality control stub."""

from pathlib import Path

from ..core.plugin import Plugin, PluginResult


class QCPlugin(Plugin):
    name = "qc"
    version = "0.1.0"
    description = "Sequence quality control — count, deduplicate, validate"

    def run(self, input_data, config=None) -> PluginResult:
        """Count sequences from a FASTA file or string input."""
        if input_data is None:
            return PluginResult(
                ok=False,
                errors=["No input provided. Pass a FASTA file path."],
            )

        path = Path(input_data) if isinstance(input_data, str) else None
        if path and path.exists():
            text = path.read_text(encoding="utf-8")
        else:
            text = str(input_data)

        seqs = [l for l in text.split("\n") if l.startswith(">")]
        count = len(seqs)

        return PluginResult(
            ok=True,
            data={
                "file": str(path) if path and path.exists() else "<stdin>",
                "sequence_count": count,
                "status": "ok" if count > 0 else "empty",
            },
            warnings=["No sequences found."] if count == 0 else [],
        )

    def validate(self) -> PluginResult:
        return PluginResult(ok=True)
