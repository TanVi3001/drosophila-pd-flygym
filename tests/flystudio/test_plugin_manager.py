from drosophila_pd.flystudio.plugin_manager import PluginManager, Plugin

def test_plugin_manager():
    manager = PluginManager()
    plugin = Plugin(id="mujoco", name="MuJoCo Renderer", version="1.0")
    manager.register_plugin(plugin)
    assert manager.get_plugin("mujoco") == plugin
    assert manager.get_plugin("unknown") is None
