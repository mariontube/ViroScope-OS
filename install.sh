#!/bin/bash
# ViroScope OS — one-command installer
# Usage: bash install.sh
set -e

BIN_DIR="$HOME/bin"
mkdir -p "$BIN_DIR"

echo "═══ ViroScope OS Installer ═══"
echo ""

# 1. Check Python
echo "[1/5] Checking Python..."
python3 --version || { echo "ERROR: Python 3.10+ required. Install from https://python.org"; exit 1; }
echo "      OK: $(python3 --version)"

# 2. Install ViroScope
echo "[2/5] Installing ViroScope..."
pip3 install -e . --quiet 2>/dev/null || pip3 install --user -e . --quiet 2>/dev/null
echo "      OK"

# 3. Nextclade
echo "[3/5] Installing Nextclade..."
if command -v nextclade &>/dev/null || [ -f "$BIN_DIR/nextclade.exe" ]; then
    echo "      Already installed: $(nextclade --version 2>/dev/null || echo 'found')"
else
    OS="$(uname -s)"
    if [ "$OS" = "Linux" ]; then
        URL="https://github.com/nextstrain/nextclade/releases/download/3.21.2/nextclade-x86_64-unknown-linux-gnu"
    elif [ "$OS" = "Darwin" ]; then
        URL="https://github.com/nextstrain/nextclade/releases/download/3.21.2/nextclade-x86_64-apple-darwin"
    else
        URL="https://github.com/nextstrain/nextclade/releases/download/3.21.2/nextclade-x86_64-pc-windows-gnu.exe"
    fi
    curl -sL -o "$BIN_DIR/nextclade" "$URL" && chmod +x "$BIN_DIR/nextclade"
    echo "      OK: $(nextclade --version 2>/dev/null || echo 'installed')"
fi

# 4. MAFFT
echo "[4/5] Installing MAFFT..."
if command -v mafft &>/dev/null; then
    echo "      Already installed: $(mafft --version 2>&1 | head -1)"
else
    echo "      Please install MAFFT manually: https://mafft.cbrc.jp/alignment/software/"
    echo "      (or: conda install -c bioconda mafft)"
fi

# 5. IQ-TREE
echo "[5/5] Installing IQ-TREE..."
if command -v iqtree3 &>/dev/null || command -v iqtree &>/dev/null || [ -f "$BIN_DIR/iqtree3" ]; then
    echo "      Already installed: $(iqtree3 --version 2>/dev/null || iqtree --version 2>/dev/null || echo 'found')"
else
    echo "      Please install IQ-TREE manually: http://www.iqtree.org/#download"
    echo "      (or: conda install -c bioconda iqtree)"
fi

echo ""
echo "═══ Installation Complete ═══"
echo ""
echo "Test: python3 -m viroscope.cli list"
echo ""
echo "Quick start:"
echo "  1. Put your FASTA sequences in data/"
echo "  2. python3 -m viroscope.cli run qc data/your_sequences.fasta"
echo "  3. python3 -m viroscope.cli run nextclade data/your_sequences.fasta -d flu_h3n2_ha"
echo "  4. python3 -m viroscope.cli run alignment data/your_sequences.fasta"
echo "  5. python3 -m viroscope.cli run tree aligned.fasta"
echo ""
