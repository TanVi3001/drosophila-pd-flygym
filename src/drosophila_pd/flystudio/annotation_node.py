from dataclasses import dataclass
from .scene_node import SceneNode

@dataclass
class AnnotationNode(SceneNode):
    """Annotation text or marker in the scene."""
    text: str = ""
    font_size: float = 12.0
