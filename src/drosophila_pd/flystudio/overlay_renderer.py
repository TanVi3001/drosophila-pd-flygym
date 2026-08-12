from abc import ABC, abstractmethod
from typing import List
from .overlays import Overlay

class OverlayRenderer(ABC):
    """Abstract interface for rendering 2D overlays over the viewport."""

    @abstractmethod
    def render_overlays(self, overlays: List[Overlay], viewport_width: int, viewport_height: int) -> None:
        """Render a list of overlays."""
        pass
