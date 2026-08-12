# Scene Graph Specification

JSON Serialization format adheres to the dataclass definitions.
All transforms are `[Tx, Ty, Tz]`, rotations `[Qw, Qx, Qy, Qz]`, and scales `[Sx, Sy, Sz]`.
Colors are normalized RGBA or RGB arrays.
Node IDs must be unique strings within the hierarchy.
