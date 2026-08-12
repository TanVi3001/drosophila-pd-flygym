from dataclasses import dataclass, field
from typing import List, Tuple

@dataclass
class PathNode:
    """A node in a cinematic camera path."""
    time: float
    position: Tuple[float, float, float]
    target: Tuple[float, float, float]

@dataclass
class CameraPath:
    """A cinematic path for a camera."""
    id: str
    nodes: List[PathNode] = field(default_factory=list)

    def evaluate(self, time: float) -> PathNode:
        """Evaluate the path at the given time to get camera state."""
        if not self.nodes:
            return PathNode(0.0, (0.0,0.0,0.0), (0.0,0.0,0.0))
        # Abstract implementation, usually involves spline interpolation
        return self.nodes[0]
