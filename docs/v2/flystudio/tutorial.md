# Tutorial

To create a new Fly Studio project:
```python
from drosophila_pd.flystudio.project import FlyStudioProject
from drosophila_pd.flystudio.scene import Actor

project = FlyStudioProject(name="My Tutorial Project")
project.scene.add_actor(Actor(id="fly1", type="mesh"))
json_data = project.to_json()
```
