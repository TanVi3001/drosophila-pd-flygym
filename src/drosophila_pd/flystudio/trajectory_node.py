from dataclasses import dataclass, field
from typing import List, Tuple
from .scene_node import SceneNode

@dataclass
class TrajectoryNode(SceneNode):
    """Trajectory visualization object and replay path."""
    points: List[Tuple[float, float, float]] = field(default_factory=list)
    color: Tuple[float, float, float] = (1.0, 0.0, 0.0)
    thickness: float = 1.0
