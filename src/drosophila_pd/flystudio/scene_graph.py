from dataclasses import dataclass, field
from typing import Dict
from .scene_node import SceneNode
from .environment import Environment
from .material import Material
from .selection import Selection

@dataclass
class SceneGraph:
    """Complete 3D scene representation."""
    root: SceneNode = field(default_factory=lambda: SceneNode(id="root", name="Root"))
    environment: Environment = field(default_factory=Environment)
    materials: Dict[str, Material] = field(default_factory=dict)
    selection: Selection = field(default_factory=Selection)
