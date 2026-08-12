from drosophila_pd.flystudio.scene_node import SceneNode

def test_scene_node():
    node1 = SceneNode(id="root")
    node2 = SceneNode(id="child")
    node1.add_child(node2)
    assert node1.id == "root"
    assert len(node1.children) == 1
    assert node1.children[0].id == "child"
