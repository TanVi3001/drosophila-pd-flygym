from drosophila_pd.flystudio.scene_graph import SceneGraph

def test_scene_graph():
    sg = SceneGraph()
    assert sg.root.id == "root"
    assert sg.environment is not None
    assert len(sg.materials) == 0
    assert len(sg.selection.selected_node_ids) == 0
