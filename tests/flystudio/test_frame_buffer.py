from drosophila_pd.flystudio.frame_buffer import FrameBuffer

def test_frame_buffer():
    fb = FrameBuffer(id="fb1", width=1920, height=1080)
    assert fb.width == 1920
    assert fb.height == 1080
    assert fb.format == "RGBA"
    fb.clear()
