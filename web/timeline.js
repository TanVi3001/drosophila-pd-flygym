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
        const keyframes = getKeyframeEntries(this.workspace, totalFrames);
        this.container.innerHTML = `
            <div class="timeline-panel">
                <div class="timeline-readout">
                    <span>Current Frame: <strong>${currentFrame}</strong></span>
                    <span>Total Frames: <strong>${totalFrames}</strong></span>
                    <span>Keyframes: <strong>${keyframes.length}</strong></span>
                    <span>Selected Keyframe: <strong>${getSelectedKeyframeFrame(this.workspace)}</strong></span>
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
                        ${keyframes.map((entry) => renderKeyframeMarker(
                            entry,
                            currentFrame,
                            this.workspace.selectedKeyframe,
                            totalFrames,
                        )).join('')}
                    </div>
                </div>
            </div>
        `;

        const panel = this.container.querySelector('.timeline-panel');
        const slider = this.container.querySelector('.timeline-slider');
        slider.addEventListener('input', (event) => {
            this.seek(Number(event.target.value));
        });
        this.container.querySelectorAll('.timeline-keyframe').forEach((marker) => {
            marker.addEventListener('click', (event) => {
                event.stopPropagation();
                const entry = keyframes.find((candidate) => (
                    candidate.frame === Number(marker.dataset.frame)
                ));
                if (entry) this.selectKeyframe(entry);
            });
        });
        slider.addEventListener('click', (event) => event.stopPropagation());
        panel.addEventListener('click', () => this.clearKeyframeSelection());
    }

    seek(frame) {
        const totalFrames = Math.max(1, this.workspace.totalFrames);
        this.workspace.currentFrame = clamp(frame, 0, totalFrames - 1);
        this.render();
        if (this.onSeekFrame) this.onSeekFrame(this.workspace.currentFrame);
    }

    selectKeyframe(entry) {
        this.workspace.selectKeyframe(entry.data, entry.frame);
        this.render();
        if (this.onSeekFrame) this.onSeekFrame(this.workspace.currentFrame);
    }

    clearKeyframeSelection() {
        if (!this.workspace.selectedKeyframe) return;
        this.workspace.clearKeyframeSelection();
        this.render();
    }
}

function getKeyframeEntries(workspace, totalFrames) {
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
    const entries = source
        .filter((entry) => !hasFlags || entry?.keyframe === true || entry?.isKeyframe === true)
        .map((entry, index) => ({
            data: entry,
            frame: getKeyframeFrame(entry, index),
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

function getKeyframeFrame(keyframe, fallback) {
    if (typeof keyframe === 'number') return Math.round(keyframe);
    if (!keyframe || typeof keyframe !== 'object') return fallback;

    const position = keyframe.frame ?? keyframe.frameIndex ?? keyframe.at;
    const frame = Number(position);
    return Number.isFinite(frame) ? Math.round(frame) : fallback;
}

function renderKeyframeMarker(entry, currentFrame, selectedKeyframe, totalFrames) {
    const percentage = totalFrames <= 1
        ? 0
        : (entry.frame / (totalFrames - 1)) * 100;
    const selected = selectedKeyframe?.frame === entry.frame ? ' selected' : '';
    const current = entry.frame === currentFrame ? ' current' : '';
    return `
        <button
            class="timeline-keyframe${selected}${current}"
            type="button"
            style="left: ${percentage}%"
            data-frame="${entry.frame}"
            aria-label="Keyframe at frame ${entry.frame}"
            title="Keyframe ${entry.frame}"
        ></button>
    `;
}

function getSelectedKeyframeFrame(workspace) {
    return workspace.selectedKeyframe
        ? workspace.selectedKeyframe.frame
        : 'None';
}

function clamp(value, minimum, maximum) {
    const numericValue = Number.isFinite(value) ? value : minimum;
    return Math.min(maximum, Math.max(minimum, Math.round(numericValue)));
}
