from drosophila_pd.flystudio.camera import Camera

def test_camera_creation():
    cam = Camera(id="cam1", type="top", position=(0.0, 0.0, 10.0), target=(0.0, 0.0, 0.0))
    assert cam.id == "cam1"
    assert cam.type == "top"
    assert cam.position == (0.0, 0.0, 10.0)
