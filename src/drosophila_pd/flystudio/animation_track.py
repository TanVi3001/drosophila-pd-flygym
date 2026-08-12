from dataclasses import dataclass, field
from typing import List, Any

@dataclass
class Keyframe:
    """A single keyframe."""
    time: float
    value: Any
    interpolation: str = "linear"

@dataclass
class AnimationTrack:
    """A track of animation keyframes targeting a specific property."""
    target: str
    keyframes: List[Keyframe] = field(default_factory=list)

    def evaluate(self, time: float) -> Any:
        """Evaluate the track value at the given time."""
        if not self.keyframes:
            return None
        for i, kf in enumerate(self.keyframes):
            if kf.time == time:
                return kf.value
            if kf.time > time:
                if i == 0:
                    return kf.value
                prev = self.keyframes[i-1]
                return prev.value
        return self.keyframes[-1].value
