from drosophila_pd.flystudio.animation import Animation
from drosophila_pd.flystudio.animation_track import AnimationTrack, Keyframe

def test_animation_evaluate():
    track = AnimationTrack(target="cam.pos", keyframes=[
        Keyframe(time=0.0, value=0.0),
        Keyframe(time=1.0, value=10.0)
    ])
    anim = Animation(id="anim1", name="Move", tracks=[track], duration=1.0)

    res = anim.evaluate(0.0)
    assert res["cam.pos"] == 0.0

    res = anim.evaluate(1.0)
    assert res["cam.pos"] == 10.0
