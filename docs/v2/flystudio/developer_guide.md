# Developer Guide

When developing rendering implementations, subclass `RendererBase` and implement `initialize`, `render_frame`, and `destroy`.
Do not import MuJoCo or rendering libraries in the core foundation. Keep it purely abstract and JSON serializable.
