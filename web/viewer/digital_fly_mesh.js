import * as THREE from 'three';
import { quaternionFromOrientation, vectorFromValue } from './joint_animator.js';

const PART_COLORS = Object.freeze({
    thorax: 0xd8915f, abdomen: 0xb86d4c, head: 0xd6a06d,
    wings: 0xb6d7e5, legs: 0x58c4dd, eyes: 0xf7f7f7, antenna: 0xf0b429,
});

/** Display mesh for the supplied DigitalFly pose; dimensions are visual defaults. */
export class DigitalFlyMesh {
    constructor() {
        this.group = new THREE.Group();
        this.group.name = 'digital-fly-mesh';
        this.parts = new Map();
        this._build();
    }

    _build() {
        this._addPart('thorax', new THREE.SphereGeometry(0.55, 24, 16), [0, 0, 0], [1, 0.75, 1]);
        this._addPart('abdomen', new THREE.SphereGeometry(0.55, 24, 16), [0, -0.75, 0], [1.2, 0.6, 0.7]);
        this._addPart('head', new THREE.SphereGeometry(0.4, 20, 14), [0, 0, 0.65], [1, 0.9, 1]);
        this._addPart('eyes', new THREE.SphereGeometry(0.1, 12, 8), [-0.25, 0.05, 0.95], [1, 1, 1]);
        this._addPart('eyes', new THREE.SphereGeometry(0.1, 12, 8), [0.25, 0.05, 0.95], [1, 1, 1]);
        [-1, 1].forEach((side) => {
            const wing = this._addPart('wings', new THREE.PlaneGeometry(1.35, 0.55), [side * 0.7, 0.05, 0.2], [1, 1, 1]);
            wing.rotation.y = side * 0.3;
            ['front', 'middle', 'hind'].forEach((legName, index) => {
                const leg = this._addPart('legs', new THREE.CylinderGeometry(0.035, 0.035, 0.85, 8), [side * (0.45 + index * 0.12), -0.25 - index * 0.25, 0]);
                leg.rotation.z = side * (0.45 + index * 0.1);
                leg.name = `leg_${side < 0 ? 'L' : 'R'}_${legName}`;
            });
            const antenna = this._addPart('antenna', new THREE.CylinderGeometry(0.018, 0.018, 0.55, 8), [side * 0.2, 0.25, 0.95]);
            antenna.rotation.x = side * 0.4;
        });
    }

    _addPart(name, geometry, position, scale = [1, 1, 1]) {
        const material = new THREE.MeshStandardMaterial({
            color: PART_COLORS[name], transparent: true, opacity: 0.82,
            roughness: 0.75, metalness: 0.05, side: THREE.DoubleSide,
        });
        const mesh = new THREE.Mesh(geometry, material);
        mesh.name = name;
        mesh.position.set(...position);
        mesh.scale.set(...scale);
        mesh.userData.bodyPart = name;
        this.group.add(mesh);
        this.parts.set(`${name}:${this.parts.size}`, mesh);
        return mesh;
    }

    updateFromFrame(frame) {
        const thorax = vectorFromValue(frame?.thorax);
        if (thorax) this.group.position.set(...thorax);
        const orientation = quaternionFromOrientation(frame?.orientation);
        if (orientation) this.group.quaternion.copy(orientation);
    }

    updateFromSnapshot(snapshot) {
        const thorax = snapshot?.bones?.find((bone) => bone.id === 'thorax');
        const position = thorax?.worldTransform?.translation;
        if (Array.isArray(position)) this.group.position.set(...position);
    }

    setPartVisibility(part, visible) {
        this.parts.forEach((mesh) => {
            if (mesh.userData.bodyPart === part) mesh.visible = Boolean(visible);
        });
    }

    setOpacity(opacity) {
        this.parts.forEach((mesh) => { mesh.material.opacity = Math.max(0, Math.min(1, Number(opacity) || 0)); });
    }

    dispose() {
        this.group.traverse((object) => { object.geometry?.dispose?.(); object.material?.dispose?.(); });
        this.group.removeFromParent();
    }
}
