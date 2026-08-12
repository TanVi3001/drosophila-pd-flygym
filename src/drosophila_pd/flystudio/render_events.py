from dataclasses import dataclass
from typing import Callable, List, Dict

@dataclass
class RenderEvent:
    """Base class for render events."""
    name: str

class EventDispatcher:
    """Dispatcher for rendering events."""
    def __init__(self):
        self.listeners: Dict[str, List[Callable]] = {}

    def subscribe(self, event_name: str, callback: Callable) -> None:
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(callback)

    def dispatch(self, event: RenderEvent) -> None:
        for callback in self.listeners.get(event.name, []):
            callback(event)
