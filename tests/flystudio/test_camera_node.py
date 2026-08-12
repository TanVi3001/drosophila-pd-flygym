from drosophila_pd.flystudio.camera_node import CameraNode

def test_camera_node():
    c = CameraNode(id="cam1", fov=45.0)
    assert c.fov == 45.0
    assert not c.orthographic
