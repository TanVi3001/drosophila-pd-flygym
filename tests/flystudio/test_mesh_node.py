from drosophila_pd.flystudio.mesh_node import MeshNode

def test_mesh_node():
    mn = MeshNode(id="mesh1", mesh_uri="path/to/mesh.obj", material_id="mat1")
    assert mn.mesh_uri == "path/to/mesh.obj"
    assert mn.material_id == "mat1"
