from dataclasses import dataclass, field
from typing import List, Tuple

@dataclass
class ViewportConfig:
    """Configuration for a single viewport."""
    id: str
    camera_id: str
    rect: Tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.0) # x, y, w, h in normalized coords
    overlays: List[str] = field(default_factory=list)

@dataclass
class ViewportLayout:
    """Layout abstraction for multiple synchronized viewports."""
    id: str
    viewports: List[ViewportConfig] = field(default_factory=list)
    synchronized: bool = True
