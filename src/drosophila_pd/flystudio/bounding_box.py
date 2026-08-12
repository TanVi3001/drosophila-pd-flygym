from dataclasses import dataclass
from typing import Tuple

@dataclass
class BoundingBox:
    """World bounding box."""
    min_pt: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    max_pt: Tuple[float, float, float] = (0.0, 0.0, 0.0)
