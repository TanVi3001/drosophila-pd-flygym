from drosophila_pd.flystudio.skeleton import Skeleton
from drosophila_pd.flystudio.joint import Joint
from drosophila_pd.flystudio.transform import Transform

def test_skeleton():
    j = Joint(id="j1", name="root")
    s = Skeleton(id="skel", root_joint=j)
    s.pose["j1"] = Transform(translation=(1.0, 0.0, 0.0))
    assert s.root_joint.id == "j1"
    assert s.pose["j1"].translation[0] == 1.0
