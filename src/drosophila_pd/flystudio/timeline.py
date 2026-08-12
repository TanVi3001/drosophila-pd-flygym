from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class Bookmark:
    """A bookmark on the timeline."""
    frame: int
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Timeline:
    """Timeline for playback control."""
    start_frame: int = 0
    end_frame: int = 0
    current_frame: int = 0
    playback_speed: float = 1.0
    playing: bool = False
    bookmarks: Dict[str, Bookmark] = field(default_factory=dict)

    def play(self) -> None:
        self.playing = True

    def pause(self) -> None:
        self.playing = False

    def seek(self, frame: int) -> None:
        self.current_frame = max(self.start_frame, min(self.end_frame, frame))
