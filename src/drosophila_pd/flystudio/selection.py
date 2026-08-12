from dataclasses import dataclass, field
from typing import List

@dataclass
class Selection:
    """Object picking abstraction."""
    selected_node_ids: List[str] = field(default_factory=list)

    def select(self, node_id: str) -> None:
        if node_id not in self.selected_node_ids:
            self.selected_node_ids.append(node_id)

    def clear(self) -> None:
        self.selected_node_ids.clear()
