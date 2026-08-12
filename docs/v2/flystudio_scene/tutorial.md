# Tutorial

Building a basic scene:
```python
from drosophila_pd.flystudio.scene_graph import SceneGraph
from drosophila_pd.flystudio.mesh_node import MeshNode
from drosophila_pd.flystudio.transform import Transform

# Create graph
scene = SceneGraph()

# Add a mesh
fly_mesh = MeshNode(id="fly", mesh_uri="assets/fly.obj")
fly_mesh.transform = Transform(translation=(0.0, 1.0, 0.0))

# Attach to root
scene.root.add_child(fly_mesh)
```
