from dataclasses import dataclass, field
from typing import Dict

@dataclass
class RenderStatistics:
    """Statistics for rendering performance and diagnostics."""
    fps: float = 0.0
    frame_timing_ms: float = 0.0
    render_timing_ms: float = 0.0
    memory_usage_mb: float = 0.0
    plugin_diagnostics: Dict[str, str] = field(default_factory=dict)

    def update(self, frame_timing_ms: float, render_timing_ms: float) -> None:
        """Update timings and compute FPS."""
        self.frame_timing_ms = frame_timing_ms
        self.render_timing_ms = render_timing_ms
        if frame_timing_ms > 0:
            self.fps = 1000.0 / frame_timing_ms
