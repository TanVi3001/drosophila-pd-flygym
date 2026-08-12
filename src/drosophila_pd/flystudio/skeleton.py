from dataclasses import dataclass, field
from typing import Dict, Optional
from .scene_node import SceneNode
from .joint import Joint
from .transform import Transform

@dataclass
class Skeleton(SceneNode):
    """Skeleton with joint hierarchy and pose container."""
    root_joint: Optional[Joint] = None
    pose: Dict[str, Transform] = field(default_factory=dict)
