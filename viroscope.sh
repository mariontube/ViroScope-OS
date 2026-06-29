#!/bin/bash
# ViroScope shortcut — run from project root
# Usage: ./viroscope.sh list
#        ./viroscope.sh run qc data/my_sequences.fasta
#        ./viroscope.sh run nextclade data/my_sequences.fasta -d flu_h3n2_ha
#        ./viroscope.sh run alignment data/my_sequences.fasta

export PATH="$HOME/bin:$PATH"
cd "$(dirname "$0")"
python3 -m viroscope.cli "$@"
