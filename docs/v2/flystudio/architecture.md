# Architecture

The Fly Studio architecture is designed around several key modules:
- Scene: Abstraction for actors and layers.
- Camera: Camera configurations (top, front, side, etc).
- Timeline: Playback control, frames, bookmarks.
- Overlays: 2D HUD elements.
- Viewport: Viewport layout and synchronization.
- RendererBase: Abstract interface for rendering implementations.
- AssetManager: Management for meshes, trajectories, videos, etc.
- Project: Serializable root container for the entire configuration.
