from drosophila_pd.flystudio.material import Material

def test_material():
    m = Material(id="mat1", name="Red", albedo=(1.0, 0.0, 0.0, 1.0))
    assert m.id == "mat1"
    assert m.albedo[0] == 1.0
