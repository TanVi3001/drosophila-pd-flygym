from dataclasses import dataclass, field
from typing import Tuple, Dict, Any

@dataclass
class Environment:
    """Scene environment settings."""
    ambient_color: Tuple[float, float, float] = (0.1, 0.1, 0.1)
    skybox_uri: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
