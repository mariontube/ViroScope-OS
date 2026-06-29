"""Config management — reads/writes .ini files from configs/."""

import configparser
from pathlib import Path


DEFAULT_CONFIG_DIR = Path(__file__).resolve().parent.parent.parent.parent / "configs"


def load(name: str, config_dir: Path | None = None) -> configparser.ConfigParser:
    """Load a named config file (configs/<name>.ini). Returns empty config if missing."""
    cfg = configparser.ConfigParser()
    path = (config_dir or DEFAULT_CONFIG_DIR) / f"{name}.ini"
    if path.exists():
        cfg.read(path, encoding="utf-8")
    return cfg


def save(cfg: configparser.ConfigParser, name: str, config_dir: Path | None = None):
    """Save config to configs/<name>.ini."""
    path = (config_dir or DEFAULT_CONFIG_DIR) / f"{name}.ini"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        cfg.write(f)
