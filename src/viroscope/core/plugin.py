"""Plugin base class — every ViroScope module inherits from this."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PluginResult:
    """Standardised return value for all plugins."""
    ok: bool
    data: Any = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class Plugin:
    """Minimal plugin interface. Override `run()` in subclasses."""

    name: str = "base"
    version: str = "0.1.0"
    description: str = ""

    def run(self, input_data: Any, config: dict | None = None) -> PluginResult:
        """Execute the plugin. Return PluginResult."""
        raise NotImplementedError(f"{self.name}: run() not implemented")

    def validate(self) -> PluginResult:
        """Check that the plugin is ready (dependencies, etc). Override as needed."""
        return PluginResult(ok=True)
