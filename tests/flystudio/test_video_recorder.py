from drosophila_pd.flystudio.video_recorder import VideoRecorder

class DummyRecorder(VideoRecorder):
    def start_recording(self, file_path, format="mp4", fps=30):
        pass
    def add_frame(self, frame_data):
        pass
    def stop_recording(self):
        pass

def test_video_recorder():
    recorder = DummyRecorder()
    recorder.start_recording("test.mp4")
    recorder.add_frame(b"data")
    recorder.stop_recording()
