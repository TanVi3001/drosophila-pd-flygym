from dataclasses import dataclass
from typing import Tuple

@dataclass
class CameraController:
    """Controller for manipulating camera state."""
    camera_id: str
    mode: str = "free" # orbit, pan, zoom, tracking, follow, cinematic
    orbit_center: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    zoom_level: float = 1.0

    def pan(self, dx: float, dy: float) -> None:
        """Pan the camera."""
        pass

    def zoom(self, delta: float) -> None:
        """Zoom the camera."""
        self.zoom_level += delta

    def orbit(self, azimuth: float, elevation: float) -> None:
        """Orbit the camera around its center."""
        pass
