export class Timeline {
    constructor(workspace, onSeekFrame = null) {
        this.workspace = workspace;
        this.container = null;
        this.onSeekFrame = onSeekFrame;
        this.dragState = null;
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
        const keyframes = this.workspace.getKeyframeEntries();
        this.container.innerHTML = `
            <div class="timeline-panel">
                <div class="timeline-readout">
                    <span class="timeline-current-frame">Current Frame: <strong>${currentFrame}</strong></span>
                    <span>Total Frames: <strong>${totalFrames}</strong></span>
                    <span>Keyframes: <strong>${keyframes.length}</strong></span>
                    <span class="timeline-selected-keyframe">Selected Keyframe: <strong>${getSelectedKeyframeFrame(this.workspace)}</strong></span>
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
                            this.workspace.selectedKeyframes,
                            totalFrames,
                        )).join('')}
                    </div>
                </div>
            </div>
        `;

        const panel = this.container.querySelector('.timeline-panel');
        const track = this.container.querySelector('.timeline-track');
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
                if (entry) this.selectKeyframe(entry, event.shiftKey);
            });
            const entry = keyframes.find((candidate) => (
                candidate.frame === Number(marker.dataset.frame)
            ));
            if (!entry) return;
            marker.addEventListener('pointerdown', (event) => (
                this.startDrag(event, entry, marker, track)
            ));
            marker.addEventListener('pointermove', (event) => this.drag(event));
            marker.addEventListener('pointerup', (event) => this.endDrag(event));
            marker.addEventListener('pointercancel', (event) => this.endDrag(event));
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

    startDrag(event, entry, marker, track) {
        if (event.button !== 0) return;
        event.preventDefault();
        event.stopPropagation();
        this.workspace.selectKeyframe(entry.data, entry.frame, entry.sourceIndex);
        this.dragState = {
            entry,
            marker,
            pointerId: event.pointerId,
            track,
            totalFrames: Math.max(1, this.workspace.totalFrames),
            startFrame: entry.frame,
        };
        marker.setPointerCapture(event.pointerId);
        this.updateMarkerState();
        if (this.onSeekFrame) this.onSeekFrame(this.workspace.currentFrame);
    }

    drag(event) {
        if (!this.dragState || event.pointerId !== this.dragState.pointerId) return;
        event.preventDefault();
        const nextFrame = this.frameFromPointer(event, this.dragState.track);
        const result = this.workspace.moveSelectedKeyframe(nextFrame, { recordHistory: false });
        if (!result?.updated) return;

        this.dragState.entry.frame = result.keyframe.frame;
        this.updateMarkerPosition(result.keyframe.frame);
        this.updateMarkerState();
        if (this.onSeekFrame) this.onSeekFrame(this.workspace.currentFrame);
    }

    endDrag(event) {
        if (!this.dragState || event.pointerId !== this.dragState.pointerId) return;
        if (this.dragState.marker.hasPointerCapture(event.pointerId)) {
            this.dragState.marker.releasePointerCapture(event.pointerId);
        }
        const { entry, startFrame } = this.dragState;
        const endFrame = entry.frame;
        if (endFrame !== startFrame) {
            this.workspace.recordCommand({
                label: 'Move keyframe',
                undo: () => this.workspace.setKeyframeFrame(entry, startFrame),
                redo: () => this.workspace.setKeyframeFrame(entry, endFrame),
            });
        }
        this.dragState = null;
    }

    frameFromPointer(event, track) {
        const bounds = track.getBoundingClientRect();
        if (bounds.width <= 0) return this.workspace.currentFrame;
        const ratio = clamp((event.clientX - bounds.left) / bounds.width, 0, 1);
        return Math.round(ratio * (Math.max(1, this.workspace.totalFrames) - 1));
    }

    updateMarkerPosition(frame) {
        if (!this.dragState) return;
        const totalFrames = this.dragState.totalFrames;
        const percentage = totalFrames <= 1
            ? 0
            : (frame / (totalFrames - 1)) * 100;
        this.dragState.marker.style.left = `${percentage}%`;
        this.dragState.marker.dataset.frame = String(frame);
        this.dragState.marker.setAttribute('aria-label', `Keyframe at frame ${frame}`);
        this.dragState.marker.title = `Keyframe ${frame}`;
        const currentReadout = this.container.querySelector('.timeline-current-frame strong');
        const selectedReadout = this.container.querySelector('.timeline-selected-keyframe strong');
        if (currentReadout) currentReadout.textContent = String(frame);
        if (selectedReadout) selectedReadout.textContent = String(frame);
    }

    updateMarkerState() {
        const currentFrame = this.workspace.currentFrame;
        const selectedKeyframes = this.workspace.selectedKeyframes;
        this.container.querySelectorAll('.timeline-keyframe').forEach((marker) => {
            const frame = Number(marker.dataset.frame);
            marker.classList.toggle('current', frame === currentFrame);
            marker.classList.toggle('selected', selectedKeyframes.some((entry) => entry.frame === frame));
        });
    }

    selectKeyframe(entry, additive = false) {
        if (additive) {
            this.workspace.toggleKeyframeSelection(entry);
        } else {
            this.workspace.selectKeyframe(entry.data, entry.frame, entry.sourceIndex);
        }
        this.render();
        if (this.onSeekFrame) this.onSeekFrame(this.workspace.currentFrame);
    }

    clearKeyframeSelection() {
        if (!this.workspace.selectedKeyframe) return;
        this.workspace.clearKeyframeSelection();
        this.render();
        if (this.onSeekFrame) this.onSeekFrame(this.workspace.currentFrame);
    }
}

function renderKeyframeMarker(entry, currentFrame, selectedKeyframes, totalFrames) {
    const percentage = totalFrames <= 1
        ? 0
        : (entry.frame / (totalFrames - 1)) * 100;
    const selected = selectedKeyframes.some((candidate) => (
        candidate.data === entry.data && candidate.sourceIndex === entry.sourceIndex
    )) ? ' selected' : '';
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
