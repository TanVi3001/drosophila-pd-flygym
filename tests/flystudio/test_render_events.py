from drosophila_pd.flystudio.render_events import EventDispatcher, RenderEvent

def test_render_events():
    dispatcher = EventDispatcher()
    event_data = []

    def on_event(evt):
        event_data.append(evt.name)

    dispatcher.subscribe("frame_ready", on_event)
    dispatcher.dispatch(RenderEvent("frame_ready"))

    assert event_data == ["frame_ready"]
