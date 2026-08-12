from dataclasses import dataclass
from typing import Tuple
from .scene_node import SceneNode

@dataclass
class LightNode(SceneNode):
    """Light node (directional, point, spot)."""
    light_type: str = "point"
    color: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    intensity: float = 1.0
    inner_cone_angle: float = 0.0
    outer_cone_angle: float = 0.785
