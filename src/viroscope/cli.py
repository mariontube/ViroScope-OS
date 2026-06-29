"""CLI entry point — `viroscope` command with subcommands."""

import argparse
import json
import sys
from pathlib import Path

from .core.loader import discover, run_plugin
from .core.config import load as load_config


def cmd_list(args):
    """List all discovered plugins."""
    plugins = discover()
    if not plugins:
        print("No plugins found.")
        return
    for name, cls in sorted(plugins.items()):
        print(f"  {name:<20} v{cls.version:<10} {cls.description}")

def cmd_run(args):
    """Run a plugin by name."""
    plugins = discover()
    if args.plugin not in plugins:
        print(f"Unknown plugin: {args.plugin}")
        print(f"Available: {', '.join(sorted(plugins))}" if plugins else "None")
        sys.exit(1)

    # Load config from file if specified
    config = {}
    if args.config:
        cfg = load_config(args.config)
        for section in cfg.sections():
            config.update({k: v for k, v in cfg[section].items()})
    # CLI overrides
    if args.dataset:
        config["dataset"] = args.dataset

    result = run_plugin(plugins[args.plugin], args.input, config)
    if result.ok:
        if result.data is not None:
            # Print JSON report nicely, skip raw output dir
            report = result.data.get("report", result.data)
            print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        for e in result.errors:
            print(f"ERROR: {e}")
        sys.exit(1)
    for w in result.warnings:
        print(f"WARNING: {w}")

def cmd_config(args):
    """Display config for a module."""
    cfg = load_config(args.name)
    for section in cfg.sections():
        print(f"[{section}]")
        for k, v in cfg[section].items():
            print(f"  {k} = {v}")

def main():
    parser = argparse.ArgumentParser(prog="viroscope", description="ViroScope OS CLI")
    parser.add_argument("--version", action="version", version="0.2.1")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="List all plugins")

    p_run = sub.add_parser("run", help="Run a plugin")
    p_run.add_argument("plugin", help="Plugin name")
    p_run.add_argument("input", nargs="?", help="Input data (file path or string)")
    p_run.add_argument("--dataset", "-d", help="Dataset name (for nextclade, etc.)")
    p_run.add_argument("--config", "-c", help="Config file name (from configs/)")

    p_cfg = sub.add_parser("config", help="Show config")
    p_cfg.add_argument("name", nargs="?", default="viroscope", help="Config name")

    args = parser.parse_args()
    if args.command == "list":
        cmd_list(args)
    elif args.command == "run":
        cmd_run(args)
    elif args.command == "config":
        cmd_config(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
