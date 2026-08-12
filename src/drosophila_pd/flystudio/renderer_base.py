from abc import ABC, abstractmethod
from typing import Any

class RendererBase(ABC):
    """Abstract interface for a renderer."""
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize renderer resources."""
        pass

    @abstractmethod
    def render_frame(self, frame: int) -> Any:
        """Render a single frame."""
        pass

    @abstractmethod
    def destroy(self) -> None:
        """Clean up renderer resources."""
        pass
