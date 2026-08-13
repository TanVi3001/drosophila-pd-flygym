export class Workspace {
    constructor() {
        this.data = {};
        this.selectedNode = null;
        this.currentFrame = 0;
        this.totalFrames = 1;
        this.animation = null;
        this.frames = [];
        this.duration = 0;
    }

    load(data = null) {
        if (data !== null) {
            this.data = data;
            this.selectedNode = null;
            this.currentFrame = 0;
            this.animation = getAnimation(data);
            this.frames = Array.isArray(this.animation?.frames)
                ? this.animation.frames
                : [];
            this.duration = getDuration(this.animation, data);
            this.totalFrames = this.frames.length > 0
                ? this.frames.length
                : getTotalFrames(data);
            console.log('Workspace updated.');
            return this.data;
        }

        console.log('Workspace loaded.');
        return this.data;
    }

    selectNode(node) {
        this.selectedNode = node || null;
        return this.selectedNode;
    }

    save() {
        console.log("Workspace saved.");
    }
}

function getTotalFrames(data) {
    const candidates = [
        data?.totalFrames,
        data?.frameCount,
        data?.scene?.totalFrames,
        data?.scene?.frameCount,
        data?.animation?.totalFrames,
        data?.animation?.frameCount,
        data?.animation?.frames?.length,
        data?.frames?.length,
        data?.scene?.animation?.totalFrames,
        data?.scene?.animation?.frames?.length,
        data?.scene?.frames?.length,
    ];

    for (const value of candidates) {
        const frames = Number(value);
        if (Number.isInteger(frames) && frames > 0) return frames;
    }
    return 1;
}

function getAnimation(data) {
    if (data?.animation && typeof data.animation === 'object') return data.animation;
    if (data?.scene?.animation && typeof data.scene.animation === 'object') {
        return data.scene.animation;
    }
    if (Array.isArray(data?.frames)) {
        return { frames: data.frames, duration: data.duration };
    }
    return null;
}

function getDuration(animation, data) {
    const duration = Number(animation?.duration ?? data?.duration ?? 0);
    return Number.isFinite(duration) && duration >= 0 ? duration : 0;
}
