from dataclasses import dataclass, field
from typing import List

@dataclass
class Visibility:
    """Visibility state and layer filtering."""
    visible: bool = True
    layers: List[str] = field(default_factory=lambda: ["default"])
