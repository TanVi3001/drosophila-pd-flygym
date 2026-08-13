export class Timeline {
    constructor(workspace, onSeekFrame = null) {
        this.workspace = workspace;
        this.container = null;
        this.onSeekFrame = onSeekFrame;
    }

    init(container) {
        this.container = container;
        this.render();
    }

    render() {
        if (!this.container) return;
        const totalFrames = Math.max(1, this.workspace.totalFrames);
        const currentFrame = clamp(
            this.workspace.currentFrame,
            0,
            totalFrames - 1,
        );
        this.workspace.currentFrame = currentFrame;
        const keyframes = getKeyframePositions(this.workspace, totalFrames);
        this.container.innerHTML = `
            <div class="timeline-panel">
                <div class="timeline-readout">
                    <span>Current Frame: <strong>${currentFrame}</strong></span>
                    <span>Total Frames: <strong>${totalFrames}</strong></span>
                    <span>Keyframes: <strong>${keyframes.length}</strong></span>
                </div>
                <div class="timeline-track">
                    <input
                        class="timeline-slider"
                        type="range"
                        min="0"
                        max="${totalFrames - 1}"
                        step="1"
                        value="${currentFrame}"
                        aria-label="Current frame"
                        ${totalFrames === 1 ? 'disabled' : ''}
                    >
                    <div class="timeline-keyframes" aria-label="Animation keyframes">
                        ${keyframes.map((frame) => renderKeyframeMarker(frame, currentFrame, totalFrames)).join('')}
                    </div>
                </div>
            </div>
        `;

        const slider = this.container.querySelector('.timeline-slider');
        slider.addEventListener('input', (event) => {
            this.seek(Number(event.target.value));
        });
        this.container.querySelectorAll('.timeline-keyframe').forEach((marker) => {
            marker.addEventListener('click', () => {
                this.seek(Number(marker.dataset.frame));
            });
        });
    }

    seek(frame) {
        const totalFrames = Math.max(1, this.workspace.totalFrames);
        this.workspace.currentFrame = clamp(frame, 0, totalFrames - 1);
        this.render();
        if (this.onSeekFrame) this.onSeekFrame(this.workspace.currentFrame);
    }
}

function getKeyframePositions(workspace, totalFrames) {
    const animation = workspace.animation;
    const explicitKeyframes = Array.isArray(animation?.keyframes);
    const source = explicitKeyframes
        ? animation.keyframes
        : Array.isArray(workspace.frames) ? workspace.frames : [];
    const hasFlags = !explicitKeyframes && source.some((entry) => (
        entry
        && typeof entry === 'object'
        && (entry.keyframe !== undefined || entry.isKeyframe !== undefined)
    ));
    const positions = source
        .filter((entry) => !hasFlags || entry?.keyframe === true || entry?.isKeyframe === true)
        .map((entry, index) => getKeyframeFrame(entry, index))
        .filter((frame) => Number.isInteger(frame) && frame >= 0)
        .map((frame) => Math.min(frame, totalFrames - 1));
    return [...new Set(positions)].sort((left, right) => left - right);
}

function getKeyframeFrame(keyframe, fallback) {
    if (typeof keyframe === 'number') return Math.round(keyframe);
    if (!keyframe || typeof keyframe !== 'object') return fallback;

    const position = keyframe.frame ?? keyframe.frameIndex ?? keyframe.at;
    const frame = Number(position);
    return Number.isFinite(frame) ? Math.round(frame) : fallback;
}

function renderKeyframeMarker(frame, currentFrame, totalFrames) {
    const percentage = totalFrames <= 1
        ? 0
        : (frame / (totalFrames - 1)) * 100;
    const selected = frame === currentFrame ? ' selected' : '';
    return `
        <button
            class="timeline-keyframe${selected}"
            type="button"
            style="left: ${percentage}%"
            data-frame="${frame}"
            aria-label="Keyframe at frame ${frame}"
            title="Keyframe ${frame}"
        ></button>
    `;
}

function clamp(value, minimum, maximum) {
    const numericValue = Number.isFinite(value) ? value : minimum;
    return Math.min(maximum, Math.max(minimum, Math.round(numericValue)));
}
