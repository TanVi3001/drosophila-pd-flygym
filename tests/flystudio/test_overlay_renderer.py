from drosophila_pd.flystudio.overlay_renderer import OverlayRenderer
from drosophila_pd.flystudio.overlays import Overlay

class DummyOverlayRenderer(OverlayRenderer):
    def render_overlays(self, overlays, w, h):
        pass

def test_overlay_renderer():
    renderer = DummyOverlayRenderer()
    renderer.render_overlays([Overlay(id="1", type="text")], 1920, 1080)
