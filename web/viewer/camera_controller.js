/** Camera state for a future viewer. It transforms the view, never the pose. */

export const CAMERA_PRESETS = Object.freeze([
    'front', 'back', 'left', 'right', 'top', 'bottom', 'isometric',
]);

export class CameraController {
    constructor() {
        this.reset();
    }

    reset() {
        this.offsetX = 0;
        this.offsetY = 0;
        this.zoom = 1;
        this.preset = 'front';
        return this;
    }

    pan(deltaX, deltaY) {
        this.offsetX += Number(deltaX) || 0;
        this.offsetY += Number(deltaY) || 0;
        return this;
    }

    setZoom(zoom) {
        this.zoom = Math.max(0.01, Number(zoom) || 1);
        return this;
    }

    setPreset(preset) {
        if (!CAMERA_PRESETS.includes(preset)) throw new RangeError(`Unknown camera preset: ${preset}`);
        this.preset = preset;
        return this;
    }

    getTransform() {
        return {
            offsetX: this.offsetX,
            offsetY: this.offsetY,
            zoom: this.zoom,
            preset: this.preset,
        };
    }
}
