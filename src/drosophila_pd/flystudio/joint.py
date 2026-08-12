from dataclasses import dataclass, field
from typing import List
from .transform import Transform

@dataclass
class Joint:
    """A skeleton joint."""
    id: str
    name: str
    local_transform: Transform = field(default_factory=Transform)
    children: List['Joint'] = field(default_factory=list)

    def add_child(self, joint: 'Joint') -> None:
        self.children.append(joint)
