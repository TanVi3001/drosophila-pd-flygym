export class Workspace {
    constructor() {
        this.data = {};
        this.selectedNode = null;
        this.currentFrame = 0;
        this.totalFrames = 1;
    }

    load(data = null) {
        if (data !== null) {
            this.data = data;
            this.selectedNode = null;
            this.currentFrame = 0;
            this.totalFrames = getTotalFrames(data);
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
