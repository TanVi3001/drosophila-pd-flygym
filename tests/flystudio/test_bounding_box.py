from drosophila_pd.flystudio.bounding_box import BoundingBox

def test_bounding_box():
    bb = BoundingBox(min_pt=(-1.0, -1.0, -1.0), max_pt=(1.0, 1.0, 1.0))
    assert bb.min_pt == (-1.0, -1.0, -1.0)
    assert bb.max_pt == (1.0, 1.0, 1.0)
