"""Plugin discovery — finds and loads ViroScope plugins."""

import importlib
import pkgutil
from pathlib import Path

from .plugin import Plugin


def discover(package_path: str = "viroscope.plugins") -> dict[str, type[Plugin]]:
    """Scan a package for Plugin subclasses. Returns {name: class}."""
    plugins: dict[str, type[Plugin]] = {}

    try:
        pkg = importlib.import_module(package_path)
    except ModuleNotFoundError:
        return plugins

    for _, mod_name, _ in pkgutil.iter_modules(pkg.__path__, pkg.__name__ + "."):
        mod = importlib.import_module(mod_name)
        for attr in dir(mod):
            obj = getattr(mod, attr)
            if (
                isinstance(obj, type)
                and issubclass(obj, Plugin)
                and obj is not Plugin
            ):
                plugins[obj.name] = obj

    return plugins


def run_plugin(plugin_cls: type[Plugin], input_data, config=None) -> "PluginResult":
    """Instantiate and run a plugin, returning its result."""
    instance = plugin_cls()
    validation = instance.validate()
    if not validation.ok:
        return validation
    return instance.run(input_data, config)
