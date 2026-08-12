from dataclasses import dataclass

@dataclass
class RenderPass:
    """An abstract rendering pass."""
    id: str
    name: str
    enabled: bool = True

    def execute(self) -> None:
        """Execute the rendering pass operations."""
        pass
