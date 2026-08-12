from drosophila_pd.flystudio.frame_exporter import FrameExporter

class DummyExporter(FrameExporter):
    def export_frame(self, frame_data, file_path, format="png"):
        pass
    def export_metadata(self, metadata, file_path):
        pass

def test_frame_exporter():
    exporter = DummyExporter()
    exporter.export_frame(b"data", "test.png")
    exporter.export_metadata({"key": "val"}, "test.json")
