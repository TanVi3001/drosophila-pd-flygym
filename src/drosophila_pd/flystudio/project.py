import json
from dataclasses import dataclass, field, asdict
from typing import Dict, Any
from .scene import Scene
from .camera import Camera
from .timeline import Timeline
from .overlays import Overlay
from .viewport import ViewportLayout
from .asset_manager import AssetManager

@dataclass
class FlyStudioProject:
    """A serializable Fly Studio project."""
    name: str
    version: str = "1.0"
    scene: Scene = field(default_factory=Scene)
    cameras: Dict[str, Camera] = field(default_factory=dict)
    timeline: Timeline = field(default_factory=Timeline)
    overlays: Dict[str, Overlay] = field(default_factory=dict)
    layouts: Dict[str, ViewportLayout] = field(default_factory=dict)
    assets: AssetManager = field(default_factory=AssetManager)
    visual_settings: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        """Serialize the project to a JSON string."""
        return json.dumps(asdict(self))
