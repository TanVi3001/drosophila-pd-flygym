from drosophila_pd.flystudio.timeline import Timeline, Bookmark

def test_timeline_playback():
    timeline = Timeline(start_frame=0, end_frame=100)
    assert not timeline.playing
    
    timeline.play()
    assert timeline.playing
    
    timeline.pause()
    assert not timeline.playing

def test_timeline_seek():
    timeline = Timeline(start_frame=0, end_frame=100)
    timeline.seek(50)
    assert timeline.current_frame == 50
    
    timeline.seek(150)
    assert timeline.current_frame == 100
    
    timeline.seek(-10)
    assert timeline.current_frame == 0
