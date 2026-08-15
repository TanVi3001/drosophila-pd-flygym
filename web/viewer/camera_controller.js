import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

export const CAMERA_PRESETS = Object.freeze([
    'front', 'back', 'left', 'right', 'top', 'bottom', 'isometric',
]);

/** Three.js camera wrapper. Pose data is never changed by camera operations. */
export class CameraController {
    constructor({ renderer = null, scene = null, domElement, onChange = null } = {}) {
        this.renderer = renderer;
        this.scene = scene;
        this.domElement = domElement;
        this.onChange = onChange;
        this.type = 'perspective';
        this.target = new THREE.Vector3(0, 0, 0);
        this.distance = 6;
        this._createCamera();
    }

    _createCamera() {
        const width = Math.max(1, this.domElement?.clientWidth ?? 1);
        const height = Math.max(1, this.domElement?.clientHeight ?? 1);
        const aspect = width / height;
        this.camera = this.type === 'orthographic'
            ? new THREE.OrthographicCamera(-aspect * 3, aspect * 3, 3, -3, 0.01, 1000)
            : new THREE.PerspectiveCamera(45, aspect, 0.01, 1000);
        this.camera.position.set(4, 3, 5);
        this.camera.lookAt(this.target);
        this._createControls();
    }

    _createControls() {
        this.controls?.dispose();
        this.controls = new OrbitControls(this.camera, this.domElement);
        this.controls.enableDamping = false;
        this.controls.screenSpacePanning = true;
        this.controls.target.copy(this.target);
        this.controls.addEventListener('change', () => this.onChange?.());
    }

    getCamera() { return this.camera; }

    setType(type) {
        if (!['perspective', 'orthographic'].includes(type) || type === this.type) return this.type;
        const previous = this.camera.position.clone();
        this.type = type;
        this._createCamera();
        this.camera.position.copy(previous);
        this.camera.lookAt(this.target);
        this.controls.target.copy(this.target);
        this.resize();
        this.onChange?.();
        return this.type;
    }

    setPreset(preset) {
        if (!CAMERA_PRESETS.includes(preset)) throw new RangeError(`Unknown camera preset: ${preset}`);
        const directions = {
            front: [0, 0.25, 1], back: [0, 0.25, -1], left: [-1, 0.25, 0],
            right: [1, 0.25, 0], top: [0, 1, 0.001], bottom: [0, -1, 0.001],
            isometric: [1, 0.75, 1],
        };
        const direction = new THREE.Vector3(...directions[preset]).normalize();
        this.camera.position.copy(this.target).addScaledVector(direction, this.distance);
        this.controls.target.copy(this.target);
        this.controls.update();
        this.onChange?.();
        return preset;
    }

    reset() {
        this.target.set(0, 0, 0);
        this.distance = 6;
        this.setPreset('isometric');
        return this;
    }

    focus(target = new THREE.Vector3(0, 0, 0), distance = this.distance) {
        this.target.copy(target);
        this.distance = Math.max(0.1, Number(distance) || 6);
        const direction = this.camera.position.clone().sub(this.controls.target).normalize();
        this.camera.position.copy(this.target).addScaledVector(direction, this.distance);
        this.controls.target.copy(this.target);
        this.controls.update();
        this.onChange?.();
    }

    resize() {
        if (!this.camera || !this.domElement) return;
        const width = Math.max(1, this.domElement.clientWidth);
        const height = Math.max(1, this.domElement.clientHeight);
        const aspect = width / height;
        if (this.camera.isPerspectiveCamera) this.camera.aspect = aspect;
        else {
            this.camera.left = -3 * aspect;
            this.camera.right = 3 * aspect;
            this.camera.top = 3;
            this.camera.bottom = -3;
        }
        this.camera.updateProjectionMatrix();
    }

    dispose() {
        this.controls?.dispose();
        this.controls = null;
    }
}
