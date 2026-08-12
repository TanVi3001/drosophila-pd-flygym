from drosophila_pd.flystudio.trajectory_node import TrajectoryNode

def test_trajectory_node():
    t = TrajectoryNode(id="traj1", points=[(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)])
    assert len(t.points) == 2
