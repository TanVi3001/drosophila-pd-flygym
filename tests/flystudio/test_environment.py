from drosophila_pd.flystudio.environment import Environment

def test_environment():
    e = Environment(ambient_color=(0.5, 0.5, 0.5))
    assert e.ambient_color == (0.5, 0.5, 0.5)
