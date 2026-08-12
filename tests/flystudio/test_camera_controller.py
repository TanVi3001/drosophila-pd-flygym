from drosophila_pd.flystudio.camera_controller import CameraController

def test_camera_controller():
    cam = CameraController(camera_id="cam1")
    cam.zoom(0.5)
    assert cam.zoom_level == 1.5
    cam.pan(1.0, 1.0)
    cam.orbit(0.1, 0.1)
