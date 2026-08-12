import json
from dataclasses import asdict
from typing import Any, Dict
from .scene_graph import SceneGraph

class SceneSerializer:
    """Serializer for the scene graph to JSON."""

    @staticmethod
    def serialize(scene: SceneGraph) -> str:
        """Serialize the scene graph to a JSON string."""
        return json.dumps(asdict(scene))

    @staticmethod
    def deserialize(json_data: str) -> Dict[str, Any]:
        """Deserialize JSON string back into a dictionary representing the scene."""
        return json.loads(json_data)
