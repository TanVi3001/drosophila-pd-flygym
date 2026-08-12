from drosophila_pd.flystudio.animation_player import AnimationPlayer
from drosophila_pd.flystudio.animation import Animation

def test_animation_player():
    anim = Animation(id="anim1", name="test", duration=1.0)
    player = AnimationPlayer(animation=anim)

    player.play()
    assert player.playing

    player.step(0.5)
    assert player.current_time == 0.5

    player.step(1.0)
    assert player.current_time == 1.0
    assert not player.playing

    player.loop = True
    player.play()
    player.step(0.5)
    assert player.current_time == 0.5
