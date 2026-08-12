from drosophila_pd.flystudio.statistics import RenderStatistics

def test_statistics():
    stats = RenderStatistics()
    stats.update(frame_timing_ms=16.666, render_timing_ms=10.0)
    assert stats.frame_timing_ms == 16.666
    assert stats.render_timing_ms == 10.0
    assert abs(stats.fps - 60.0) < 1.0
