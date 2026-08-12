from dataclasses import dataclass, field
from typing import Dict, Type
from .renderer_base import RendererBase

@dataclass
class RendererMetadata:
    """Metadata for a registered renderer class."""
    id: str
    name: str
    version: str
    capabilities: Dict[str, bool] = field(default_factory=dict)
    renderer_class: Type[RendererBase] = None

@dataclass
class RendererRegistry:
    """Registry for discovering and instantiating renderer backends."""
    renderers: Dict[str, RendererMetadata] = field(default_factory=dict)

    def register(self, metadata: RendererMetadata) -> None:
        """Register a renderer implementation (e.g. MuJoCo, Three.js)."""
        self.renderers[metadata.id] = metadata

    def create_renderer(self, renderer_id: str) -> RendererBase:
        """Instantiate a renderer."""
        meta = self.renderers.get(renderer_id)
        if meta and meta.renderer_class:
            return meta.renderer_class()
        return None
