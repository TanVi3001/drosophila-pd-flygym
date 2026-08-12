from drosophila_pd.flystudio.transform import Transform

def test_transform():
    t = Transform()
    assert t.translation == (0.0, 0.0, 0.0)
    assert t.rotation == (1.0, 0.0, 0.0, 0.0)
    assert t.scale == (1.0, 1.0, 1.0)
