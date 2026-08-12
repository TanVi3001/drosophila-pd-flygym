from abc import ABC, abstractmethod
from typing import Dict, Any

class FrameExporter(ABC):
    """Abstract interface for exporting individual frames."""

    @abstractmethod
    def export_frame(self, frame_data: bytes, file_path: str, format: str = "png") -> None:
        """Export a frame. Supported formats: png, svg, pdf."""
        pass

    @abstractmethod
    def export_metadata(self, metadata: Dict[str, Any], file_path: str) -> None:
        """Export JSON metadata associated with the frame."""
        pass
