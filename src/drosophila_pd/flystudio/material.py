from dataclasses import dataclass, field
from typing import Tuple, Dict, Any

@dataclass
class Material:
    """Surface material properties."""
    id: str
    name: str = ""
    albedo: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)
    roughness: float = 0.5
    metallic: float = 0.0
    texture_uri: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
