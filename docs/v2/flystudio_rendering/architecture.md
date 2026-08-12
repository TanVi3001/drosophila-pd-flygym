# Rendering Architecture

The rendering core is designed around the following architectural pillars:
- **Render Pipeline & Passes**: Modular execution flow via `RenderPipeline` and `RenderPass`.
- **Animation System**: Keyframe-based animation tracks, timelines, and an `AnimationPlayer` for playback control (loop, reverse, pause).
- **Camera System**: Abstractions for `CameraController` (orbit, pan, zoom) and `CameraPath` (cinematic paths).
- **Video & Frame Export**: Abstract interfaces `VideoRecorder` and `FrameExporter` for exporting to PNG, MP4, WebM, etc. without tying to a specific encoder.
- **Plugin System**: `PluginManager` and `RendererRegistry` for dynamic discovery and registration of rendering backends.
- **Events & Diagnostics**: `EventDispatcher` for rendering lifecycle events and `RenderStatistics` for FPS and memory counters.
