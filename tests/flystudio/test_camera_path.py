from drosophila_pd.flystudio.camera_path import CameraPath, PathNode

def test_camera_path():
    path = CameraPath(id="path1", nodes=[
        PathNode(0.0, (0,0,0), (0,0,0)),
        PathNode(1.0, (1,1,1), (0,0,0))
    ])
    node = path.evaluate(0.5)
    assert node.time == 0.0
