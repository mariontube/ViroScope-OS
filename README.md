# ViroScope OS

> AI-powered virus research operating system — starting with influenza.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## What is ViroScope OS?

A modular, AI-native research platform for computational virology. Designed to replace scattered scripts with a structured, reproducible pipeline: **QC → Alignment → Tree → Annotation → Visualization → AI Report**.

## Supported Viruses (Roadmap)

| Virus | Stage | Status |
|-------|-------|--------|
| Influenza A (H1/H3/H5) | Phase 2 | 🔜 |
| IHNV | Phase 3 | 📋 |
| NDV | Phase 3 | 📋 |
| SARS-CoV-2 | Phase 4 | 📋 |

## Architecture

Plugin-based. Each analysis module is independent, with standardized I/O interfaces.

```
Core → [QC] → [Alignment] → [Tree] → [Annotation] → [Visualization] → [Report] → [AI]
```

## Quick Start

> Phase 1: Framework development. Check back soon.

## Documentation

All design docs live in [`docs/`](docs/):

| Doc | Purpose |
|-----|---------|
| [PROJECT.md](docs/PROJECT.md) | What is this project? |
| [VISION.md](docs/VISION.md) | 5-year plan |
| [ROADMAP.md](docs/ROADMAP.md) | Development roadmap |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Plugin architecture |
| [MODULE_SPEC.md](docs/MODULE_SPEC.md) | Module I/O specs |
| [RESEARCH_SPEC.md](docs/RESEARCH_SPEC.md) | Research standards (AI must follow) |
| [AI_GUIDE.md](docs/AI_GUIDE.md) | AI Agent system design |

## Development

- **Language**: Python 3.10+
- **Platform**: Linux (AutoDL)
- **Philosphy**: Phase 0 is documentation-first — no code until the design is right.

## License

MIT — free for academic and commercial use.
