import * as THREE from 'three';
import { addViewerLighting } from './lighting.js';

export class DigitalFlyScene {
    constructor() {
        this.scene = new THREE.Scene();
        this.backgroundTexture = createBackdropTexture();
        this.scene.background = this.backgroundTexture ?? new THREE.Color(0x1a232d);
        this.scene.fog = new THREE.Fog(0x4c5b66, 24, 72);
        this.root = new THREE.Group();
        this.root.name = 'digital-fly-root';
        this.scene.add(this.root);

        this.ground = new THREE.Mesh(
            new THREE.PlaneGeometry(48, 48),
            new THREE.MeshStandardMaterial({
                color: 0x9aa2a3,
                roughness: 0.96,
                metalness: 0,
            }),
        );
        this.ground.position.z = 0;
        this.ground.name = 'ground';
        this.ground.receiveShadow = true;
        this.scene.add(this.ground);
        this.grid = new THREE.GridHelper(48, 48, 0x4a5b66, 0x27343d);
        this.grid.name = 'grid';
        this.grid.rotation.x = Math.PI / 2;
        this.grid.position.z = 0.002;
        const gridMaterials = Array.isArray(this.grid.material) ? this.grid.material : [this.grid.material];
        gridMaterials.forEach((material) => {
            material.transparent = true;
            material.opacity = 0.3;
            material.depthWrite = false;
        });
        this.scene.add(this.grid);
        this.axes = new THREE.AxesHelper(2);
        this.axes.name = 'axes';
        this.scene.add(this.axes);
        this.lights = addViewerLighting(this.scene);
        this.shadowEnabled = true;
    }

    setGroundVisible(visible) { this.ground.visible = Boolean(visible); }
    setGridVisible(visible) { this.grid.visible = Boolean(visible); }
    setAxesVisible(visible) { this.axes.visible = Boolean(visible); }
    setShadowEnabled(visible) {
        this.shadowEnabled = Boolean(visible);
        this.ground.receiveShadow = this.shadowEnabled;
        Object.values(this.lights).forEach((light) => {
            if ('castShadow' in light) light.castShadow = this.shadowEnabled && light.name === 'key-light';
        });
    }

    dispose() {
        this.scene.traverse((object) => {
            object.geometry?.dispose?.();
            if (Array.isArray(object.material)) object.material.forEach((material) => material.dispose?.());
            else object.material?.dispose?.();
        });
        this.backgroundTexture?.dispose?.();
    }
}

function createBackdropTexture() {
    if (typeof document === 'undefined') return null;
    const canvas = document.createElement('canvas');
    canvas.width = 2;
    canvas.height = 512;
    const context = canvas.getContext('2d');
    if (!context) return null;
    const gradient = context.createLinearGradient(0, 0, 0, canvas.height);
    gradient.addColorStop(0, '#111923');
    gradient.addColorStop(0.45, '#2c3a46');
    gradient.addColorStop(1, '#65737a');
    context.fillStyle = gradient;
    context.fillRect(0, 0, canvas.width, canvas.height);
    const texture = new THREE.CanvasTexture(canvas);
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.needsUpdate = true;
    return texture;
}
