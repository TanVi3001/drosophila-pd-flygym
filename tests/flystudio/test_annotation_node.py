from drosophila_pd.flystudio.annotation_node import AnnotationNode

def test_annotation_node():
    a = AnnotationNode(id="ann1", text="Hello", font_size=14.0)
    assert a.text == "Hello"
    assert a.font_size == 14.0
