import json
from drosophila_pd.flystudio.project import FlyStudioProject
from drosophila_pd.flystudio.scene import Actor

def test_project_serialization():
    project = FlyStudioProject(name="Test Project")
    project.scene.add_actor(Actor(id="actor1", type="mesh"))
    
    json_str = project.to_json()
    data = json.loads(json_str)
    
    assert data["name"] == "Test Project"
    assert data["version"] == "1.0"
    assert "actor1" in data["scene"]["actors"]
