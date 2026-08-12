from dataclasses import dataclass, field
from typing import Dict, Any, Tuple

@dataclass
class Camera:
    """Camera configuration and state."""
    id: str
    type: str  # e.g., 'top', 'front', 'side', 'free', 'tracking', 'cinematic'
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    target: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    up: Tuple[float, float, float] = (0.0, 0.0, 1.0)
    properties: Dict[str, Any] = field(default_factory=dict)
