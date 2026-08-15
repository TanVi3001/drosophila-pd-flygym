import * as THREE from 'three';
import { addViewerLighting } from './lighting.js';

export class DigitalFlyScene {
    constructor() {
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0b0f14);
        this.root = new THREE.Group();
        this.root.name = 'digital-fly-root';
        this.scene.add(this.root);

        this.ground = new THREE.Mesh(
            new THREE.PlaneGeometry(30, 30),
            new THREE.MeshStandardMaterial({ color: 0x172027, roughness: 0.95, metalness: 0 }),
        );
        this.ground.rotation.x = -Math.PI / 2;
        this.ground.name = 'ground';
        this.scene.add(this.ground);
        this.grid = new THREE.GridHelper(30, 30, 0x42515d, 0x253139);
        this.grid.name = 'grid';
        this.scene.add(this.grid);
        this.axes = new THREE.AxesHelper(2);
        this.axes.name = 'axes';
        this.scene.add(this.axes);
        addViewerLighting(this.scene);
    }

    setGroundVisible(visible) { this.ground.visible = Boolean(visible); }
    setGridVisible(visible) { this.grid.visible = Boolean(visible); }
    setAxesVisible(visible) { this.axes.visible = Boolean(visible); }

    dispose() {
        this.scene.traverse((object) => {
            object.geometry?.dispose?.();
            if (Array.isArray(object.material)) object.material.forEach((material) => material.dispose?.());
            else object.material?.dispose?.();
        });
    }
}
