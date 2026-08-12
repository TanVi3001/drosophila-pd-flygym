from dataclasses import dataclass, field
from typing import Dict, Any, Tuple

@dataclass
class Overlay:
    """2D overlay element for the viewport."""
    id: str
    type: str
    visible: bool = True
    position_screen: Tuple[float, float] = (0.0, 0.0)
    properties: Dict[str, Any] = field(default_factory=dict)
