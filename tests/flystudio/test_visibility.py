from drosophila_pd.flystudio.visibility import Visibility

def test_visibility():
    v = Visibility()
    assert v.visible is True
    assert v.layers == ["default"]
