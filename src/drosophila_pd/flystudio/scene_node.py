from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .transform import Transform
from .visibility import Visibility
from .bounding_box import BoundingBox

@dataclass
class SceneNode:
    """Base scene graph node."""
    id: str
    name: str = ""
    transform: Transform = field(default_factory=Transform)
    world_transform: Transform = field(default_factory=Transform)
    visibility: Visibility = field(default_factory=Visibility)
    bounding_box: Optional[BoundingBox] = None
    children: List['SceneNode'] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)

    def add_child(self, node: 'SceneNode') -> None:
        self.children.append(node)
