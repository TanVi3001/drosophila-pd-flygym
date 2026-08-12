from drosophila_pd.flystudio.joint import Joint

def test_joint():
    j1 = Joint(id="j1", name="root")
    j2 = Joint(id="j2", name="child")
    j1.add_child(j2)
    assert j1.id == "j1"
    assert len(j1.children) == 1
