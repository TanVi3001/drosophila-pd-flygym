# Developer Guide

When developing rendering engines for Fly Studio:
- Implement `RendererBase` and register it using `RendererRegistry.register()`.
- Use `PluginManager` to manage lifecycle and capabilities of the plugin.
- Do not add direct dependencies on rendering engines (like MuJoCo or OpenGL) to the core package.
- All classes must remain purely abstract and rely on the registry for instantiation.
