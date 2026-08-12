# Tutorial

To register a new renderer plugin:
```python
from drosophila_pd.flystudio.renderer_registry import RendererRegistry, RendererMetadata
from drosophila_pd.flystudio.renderer_base import RendererBase

class MyRenderer(RendererBase):
    def initialize(self): pass
    def render_frame(self, frame): return None
    def destroy(self): pass

registry = RendererRegistry()
meta = RendererMetadata(
    id="my_renderer",
    name="My Renderer",
    version="1.0",
    renderer_class=MyRenderer
)
registry.register(meta)
renderer = registry.create_renderer("my_renderer")
```
