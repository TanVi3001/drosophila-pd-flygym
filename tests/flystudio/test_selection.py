from drosophila_pd.flystudio.selection import Selection

def test_selection():
    s = Selection()
    s.select("node1")
    assert "node1" in s.selected_node_ids
    s.select("node1") # duplicate
    assert len(s.selected_node_ids) == 1
    s.clear()
    assert len(s.selected_node_ids) == 0
