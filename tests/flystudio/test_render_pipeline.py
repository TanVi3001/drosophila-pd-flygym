from drosophila_pd.flystudio.render_pipeline import RenderPipeline
from drosophila_pd.flystudio.render_pass import RenderPass

def test_render_pipeline():
    class DummyPass(RenderPass):
        def __init__(self, id, name):
            super().__init__(id, name)
            self.executed = False
        def execute(self):
            self.executed = True

    p1 = DummyPass("1", "pass1")
    p2 = DummyPass("2", "pass2")
    p2.enabled = False

    pipeline = RenderPipeline(passes=[p1, p2])
    pipeline.execute()

    assert p1.executed is True
    assert p2.executed is False
