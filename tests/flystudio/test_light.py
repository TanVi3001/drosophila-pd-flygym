from drosophila_pd.flystudio.light import LightNode

def test_light():
    l = LightNode(id="light1", light_type="spot")
    assert l.light_type == "spot"
    assert l.color == (1.0, 1.0, 1.0)
