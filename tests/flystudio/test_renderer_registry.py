from drosophila_pd.flystudio.renderer_registry import RendererRegistry, RendererMetadata
from drosophila_pd.flystudio.renderer_base import RendererBase

class DummyRenderer(RendererBase):
    def initialize(self): pass
    def render_frame(self, frame): return None
    def destroy(self): pass

def test_renderer_registry():
    registry = RendererRegistry()
    meta = RendererMetadata(id="dummy", name="Dummy", version="1.0", renderer_class=DummyRenderer)
    registry.register(meta)

    renderer = registry.create_renderer("dummy")
    assert isinstance(renderer, DummyRenderer)
