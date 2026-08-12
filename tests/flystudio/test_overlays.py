from drosophila_pd.flystudio.overlays import Overlay

def test_overlay_creation():
    overlay = Overlay(id="hud", type="text", position_screen=(10.0, 10.0))
    assert overlay.id == "hud"
    assert overlay.visible is True
