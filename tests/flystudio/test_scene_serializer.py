import json
from drosophila_pd.flystudio.scene_serializer import SceneSerializer
from drosophila_pd.flystudio.scene_graph import SceneGraph

def test_scene_serializer():
    sg = SceneGraph()
    json_str = SceneSerializer.serialize(sg)
    assert isinstance(json_str, str)

    data = SceneSerializer.deserialize(json_str)
    assert data["root"]["id"] == "root"
