from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class Actor:
    """An actor in the visualization scene."""
    id: str
    type: str
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Layer:
    """A layer for grouping actors."""
    id: str
    name: str
    visible: bool = True
    actors: List[str] = field(default_factory=list)

@dataclass
class Scene:
    """Visualization scene abstraction."""
    actors: Dict[str, Actor] = field(default_factory=dict)
    layers: Dict[str, Layer] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_actor(self, actor: Actor, layer_id: str = "default") -> None:
        """Register an actor to the scene and optionally add to a layer."""
        self.actors[actor.id] = actor
        if layer_id not in self.layers:
            self.layers[layer_id] = Layer(id=layer_id, name=layer_id)
        if actor.id not in self.layers[layer_id].actors:
            self.layers[layer_id].actors.append(actor.id)
