from dataclasses import dataclass
from .animation import Animation

@dataclass
class AnimationPlayer:
    """Player for managing animation playback state."""
    animation: Animation
    current_time: float = 0.0
    playback_speed: float = 1.0
    playing: bool = False
    loop: bool = False
    reverse: bool = False

    def play(self) -> None:
        self.playing = True

    def pause(self) -> None:
        self.playing = False

    def step(self, delta_time: float) -> None:
        if not self.playing:
            return
        direction = -1 if self.reverse else 1
        self.current_time += delta_time * self.playback_speed * direction

        if self.loop:
            if self.current_time > self.animation.duration:
                self.current_time %= self.animation.duration
            elif self.current_time < 0:
                if self.animation.duration > 0:
                    self.current_time = self.animation.duration + (self.current_time % self.animation.duration)
                else:
                    self.current_time = 0.0
        else:
            if self.current_time > self.animation.duration:
                self.current_time = self.animation.duration
                self.pause()
            elif self.current_time < 0:
                self.current_time = 0.0
                self.pause()
