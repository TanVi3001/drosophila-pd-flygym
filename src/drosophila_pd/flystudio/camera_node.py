from dataclasses import dataclass
from .scene_node import SceneNode

@dataclass
class CameraNode(SceneNode):
    """Camera node within the scene graph."""
    fov: float = 60.0
    near_clip: float = 0.1
    far_clip: float = 1000.0
    orthographic: bool = False
