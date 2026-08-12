from dataclasses import dataclass, field
from typing import List
from .animation_track import AnimationTrack

@dataclass
class Animation:
    """An animation consisting of multiple tracks."""
    id: str
    name: str
    tracks: List[AnimationTrack] = field(default_factory=list)
    duration: float = 0.0

    def evaluate(self, time: float) -> dict:
        """Evaluate all tracks at the given time."""
        results = {}
        for track in self.tracks:
            results[track.target] = track.evaluate(time)
        return results
