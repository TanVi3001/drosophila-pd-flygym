export class Workspace {
    constructor() {
        this.data = {};
        this.selectedNode = null;
        this.selectedKeyframe = null;
        this.currentFrame = 0;
        this.totalFrames = 1;
        this.animation = null;
        this.frames = [];
        this.duration = 0;
        this.playbackState = 'Stopped';
    }

    load(data = null) {
        if (data !== null) {
            this.data = data;
            this.selectedNode = null;
            this.selectedKeyframe = null;
            this.currentFrame = 0;
            this.playbackState = 'Stopped';
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

    selectKeyframe(keyframe, frame, sourceIndex = null) {
        const selectedFrame = Number(frame);
        if (!Number.isInteger(selectedFrame) || selectedFrame < 0) {
            this.selectedKeyframe = null;
            return this.selectedKeyframe;
        }

        this.selectedKeyframe = {
            frame: selectedFrame,
            data: keyframe,
            sourceIndex,
        };
        this.currentFrame = selectedFrame;
        return this.selectedKeyframe;
    }

    clearKeyframeSelection() {
        this.selectedKeyframe = null;
        return this.selectedKeyframe;
    }

    getKeyframeEntries() {
        const explicitKeyframes = Array.isArray(this.animation?.keyframes);
        const source = explicitKeyframes
            ? this.animation.keyframes
            : Array.isArray(this.frames) ? this.frames : [];
        const hasFlags = !explicitKeyframes && source.some((entry) => (
            entry
            && typeof entry === 'object'
            && (entry.keyframe !== undefined || entry.isKeyframe !== undefined)
        ));
        const totalFrames = Math.max(1, this.totalFrames);
        const entries = source
            .filter((entry) => !hasFlags || entry?.keyframe === true || entry?.isKeyframe === true)
            .map((entry, sourceIndex) => ({
                data: entry,
                frame: getKeyframeFrame(entry, sourceIndex),
                sourceIndex,
            }))
            .filter((entry) => Number.isInteger(entry.frame) && entry.frame >= 0)
            .map((entry) => ({
                ...entry,
                frame: Math.min(entry.frame, totalFrames - 1),
            }));
        const uniqueEntries = new Map();
        entries.forEach((entry) => {
            if (!uniqueEntries.has(entry.frame)) uniqueEntries.set(entry.frame, entry);
        });
        return [...uniqueEntries.values()].sort((left, right) => left.frame - right.frame);
    }

    moveSelectedKeyframe(frame) {
        if (!this.selectedKeyframe) return null;

        const parsedFrame = Number(frame);
        if (!Number.isInteger(parsedFrame) || parsedFrame < 0) {
            return { updated: false, reason: 'invalid-frame', keyframe: this.selectedKeyframe };
        }

        const maximumFrame = Math.max(0, this.totalFrames - 1);
        const nextFrame = Math.min(parsedFrame, maximumFrame);
        const collision = this.getKeyframeEntries().some((entry) => (
            entry.frame === nextFrame
            && entry.data !== this.selectedKeyframe.data
            && entry.sourceIndex !== this.selectedKeyframe.sourceIndex
        ));
        if (collision) {
            return { updated: false, reason: 'collision', keyframe: this.selectedKeyframe };
        }

        const data = this.selectedKeyframe.data;
        if (data && typeof data === 'object' && !Array.isArray(data)) {
            const positionKey = getPositionKey(data) || 'frame';
            data[positionKey] = nextFrame;
        }

        this.selectedKeyframe.frame = nextFrame;
        this.currentFrame = nextFrame;
        return { updated: true, keyframe: this.selectedKeyframe };
    }

    updateSelectedKeyframeFrame(frame) {
        const result = this.moveSelectedKeyframe(frame);
        return result?.keyframe ?? null;
    }

    updateSelectedKeyframeMetadata(metadata) {
        if (!this.selectedKeyframe) return null;
        const data = this.selectedKeyframe.data;
        if (!data || typeof data !== 'object' || Array.isArray(data)) {
            return this.selectedKeyframe;
        }

        if (metadata === undefined) {
            delete data.metadata;
        } else {
            data.metadata = metadata;
        }
        return this.selectedKeyframe;
    }

    updateSelectedKeyframeDuration(duration) {
        if (!this.selectedKeyframe) return null;

        const parsedDuration = Number(duration);
        if (!Number.isFinite(parsedDuration) || parsedDuration < 0) {
            return this.selectedKeyframe;
        }

        const data = this.selectedKeyframe.data;
        if (data && typeof data === 'object' && !Array.isArray(data)
            && hasOwn(data, 'duration')) {
            data.duration = parsedDuration;
        } else if (this.animation && hasOwn(this.animation, 'duration')) {
            this.animation.duration = parsedDuration;
            this.duration = parsedDuration;
        }
        return this.selectedKeyframe;
    }

    save() {
        console.log("Workspace saved.");
    }
}

function getPositionKey(data) {
    return ['frame', 'frameIndex', 'at'].find((key) => hasOwn(data, key));
}

function getKeyframeFrame(keyframe, fallback) {
    if (typeof keyframe === 'number') return Math.round(keyframe);
    if (!keyframe || typeof keyframe !== 'object') return fallback;

    const position = keyframe.frame ?? keyframe.frameIndex ?? keyframe.at;
    const frame = Number(position);
    return Number.isFinite(frame) ? Math.round(frame) : fallback;
}

function hasOwn(object, key) {
    return Object.prototype.hasOwnProperty.call(object, key);
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
        getKeyframeFrameCount(data?.animation?.keyframes),
        data?.frames?.length,
        data?.scene?.animation?.totalFrames,
        data?.scene?.animation?.frames?.length,
        getKeyframeFrameCount(data?.scene?.animation?.keyframes),
        data?.scene?.frames?.length,
    ];

    for (const value of candidates) {
        const frames = Number(value);
        if (Number.isInteger(frames) && frames > 0) return frames;
    }
    return 1;
}

function getKeyframeFrameCount(keyframes) {
    if (!Array.isArray(keyframes) || keyframes.length === 0) return 0;

    const positions = keyframes.map((keyframe, index) => {
        const position = keyframe?.frame ?? keyframe?.frameIndex ?? keyframe?.at;
        const frame = Number(position);
        return Number.isInteger(frame) && frame >= 0 ? frame : index;
    });
    return Math.max(...positions) + 1;
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
