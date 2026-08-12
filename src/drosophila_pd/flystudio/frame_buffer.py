from dataclasses import dataclass

@dataclass
class FrameBuffer:
    """Abstract frame buffer for rendering output."""
    id: str
    width: int
    height: int
    format: str = "RGBA"

    def clear(self) -> None:
        """Clear the frame buffer."""
        pass
