from drosophila_pd.flystudio.scene import Scene, Actor, Layer

def test_scene_add_actor():
    scene = Scene()
    actor = Actor(id="test_actor", type="mesh")
    scene.add_actor(actor, layer_id="main")
    
    assert "test_actor" in scene.actors
    assert scene.actors["test_actor"] == actor
    assert "main" in scene.layers
    assert "test_actor" in scene.layers["main"].actors
