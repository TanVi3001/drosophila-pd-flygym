from dataclasses import dataclass, field
from typing import List
from .render_pass import RenderPass

@dataclass
class RenderPipeline:
    """A rendering pipeline consisting of multiple passes."""
    passes: List[RenderPass] = field(default_factory=list)

    def execute(self) -> None:
        """Execute all render passes in the pipeline."""
        for p in self.passes:
            if p.enabled:
                p.execute()
