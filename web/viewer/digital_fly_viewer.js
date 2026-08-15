import { CameraController } from './camera_controller.js';
import { ViewerPlaybackController } from './playback_controller.js';
import { SceneBuilder } from './scene_builder.js';
import { SkeletonAnimator } from './skeleton_animator.js';
import { TrajectoryRenderer } from './trajectory_renderer.js';
import { loadPoseJSON } from './pose_loader.js';

/** Composition root for the additive pose viewer skeleton. */
export class DigitalFlyViewer {
    constructor({ canvas = null, context = null } = {}) {
        this.canvas = canvas;
        this.context = context ?? canvas?.getContext?.('2d') ?? null;
        this.animator = new SkeletonAnimator();
        this.camera = new CameraController();
        this.playback = new ViewerPlaybackController();
        this.sceneBuilder = new SceneBuilder();
        this.trajectoryRenderer = new TrajectoryRenderer();
    }

    async load(input) {
        this.animator.setPoseDocument(await loadPoseJSON(input));
        return this.render();
    }

    setFrame(frame) {
        this.animator.frameAt(frame);
        return this.render();
    }

    render() {
        const frame = this.animator.frameAt();
        const scene = this.sceneBuilder.build(frame);
        if (this.context && this.canvas) {
            this.trajectoryRenderer.clear(this.context, this.canvas);
            this.trajectoryRenderer.render(this.context, this.canvas, scene?.trajectory, this.camera.getTransform());
        }
        return scene;
    }

    reset() {
        this.animator.clear();
        this.camera.reset();
        this.trajectoryRenderer.clear(this.context, this.canvas);
    }
}
