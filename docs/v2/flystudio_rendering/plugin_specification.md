# Plugin Specification

A valid Fly Studio rendering plugin must provide:
- A unique `id` and semantic `version`.
- A dictionary of `capabilities` (e.g., `{"video_export": True, "shadows": False}`).
- Subclasses of abstract interfaces like `RendererBase`, `VideoRecorder`, or `FrameExporter` where applicable.
