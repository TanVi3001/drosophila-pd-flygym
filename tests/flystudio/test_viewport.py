from drosophila_pd.flystudio.viewport import ViewportLayout, ViewportConfig

def test_viewport_layout():
    vp = ViewportConfig(id="vp1", camera_id="cam1")
    layout = ViewportLayout(id="layout1", viewports=[vp])
    assert layout.id == "layout1"
    assert len(layout.viewports) == 1
