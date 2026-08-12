from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class Asset:
    """An asset managed by the platform."""
    id: str
    type: str # e.g., 'mesh', 'trajectory', 'annotation', 'video', 'texture', 'metadata'
    uri: str
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AssetManager:
    """Generic management of assets."""
    assets: Dict[str, Asset] = field(default_factory=dict)

    def register_asset(self, asset: Asset) -> None:
        """Register an asset with the manager."""
        self.assets[asset.id] = asset
