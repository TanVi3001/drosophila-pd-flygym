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
        this.container.innerHTML = `
            <div class="timeline-panel">
                <div class="timeline-readout">
                    <span>Current Frame: <strong>${currentFrame}</strong></span>
                    <span>Total Frames: <strong>${totalFrames}</strong></span>
                </div>
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
            </div>
        `;

        const slider = this.container.querySelector('.timeline-slider');
        slider.addEventListener('input', (event) => {
            this.seek(Number(event.target.value));
        });
    }

    seek(frame) {
        const totalFrames = Math.max(1, this.workspace.totalFrames);
        this.workspace.currentFrame = clamp(frame, 0, totalFrames - 1);
        this.render();
        if (this.onSeekFrame) this.onSeekFrame(this.workspace.currentFrame);
    }
}

function clamp(value, minimum, maximum) {
    const numericValue = Number.isFinite(value) ? value : minimum;
    return Math.min(maximum, Math.max(minimum, Math.round(numericValue)));
}
