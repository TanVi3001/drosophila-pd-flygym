from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class Plugin:
    """A registered plugin."""
    id: str
    name: str
    version: str
    capabilities: Dict[str, bool] = field(default_factory=dict)
    instance: Any = None

@dataclass
class PluginManager:
    """Manager for dynamic discovery and lifecycle of plugins."""
    plugins: Dict[str, Plugin] = field(default_factory=dict)

    def register_plugin(self, plugin: Plugin) -> None:
        """Register a new plugin."""
        self.plugins[plugin.id] = plugin

    def get_plugin(self, plugin_id: str) -> Plugin:
        """Get a registered plugin."""
        return self.plugins.get(plugin_id)
