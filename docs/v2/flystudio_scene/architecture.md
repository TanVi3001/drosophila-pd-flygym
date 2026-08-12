# Architecture

- **Node Hierarchy**: `SceneNode` base class allows unlimited parent-child nesting.
- **Transforms**: Translation, rotation (quaternions), and scale are attached to each node.
- **Specialized Nodes**:
  - `MeshNode`: References external meshes and materials.
  - `Skeleton` & `Joint`: Defines rigging and pose storage.
  - `CameraNode`: Intrinsic camera parameters (FOV, clip planes).
  - `LightNode`: Illumination properties.
  - `TrajectoryNode`: Spatial replays.
  - `AnnotationNode`: 3D text/markers.
- **Global Context**: `Environment`, `Material` registry, and `Selection` abstractions live at the root `SceneGraph` level.
