from dataclasses import dataclass
from .scene_node import SceneNode

@dataclass
class MeshNode(SceneNode):
    """Generic mesh reference node."""
    mesh_uri: str = ""
    material_id: str = ""
