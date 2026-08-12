from drosophila_pd.flystudio.renderer_base import RendererBase

class DummyRenderer(RendererBase):
    def initialize(self):
        pass
    def render_frame(self, frame):
        return f"frame_{frame}"
    def destroy(self):
        pass

def test_renderer_base():
    renderer = DummyRenderer()
    renderer.initialize()
    assert renderer.render_frame(10) == "frame_10"
    renderer.destroy()
