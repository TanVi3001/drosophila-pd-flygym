/** UI controls for the Three.js viewer. Playback timing stays in viewer.js. */
export class TimelineController {
    constructor({ onFrame = null, onPlay = null, onPause = null, onStop = null, onSpeed = null, onLoop = null, onReset = null } = {}) {
        this.root = null;
        this.frameInput = null;
        this.frameReadout = null;
        this.totalReadout = null;
        this.playButton = null;
        this.pauseButton = null;
        this.stopButton = null;
        this.speedInput = null;
        this.loopInput = null;
        this.callbacks = { onFrame, onPlay, onPause, onStop, onSpeed, onLoop, onReset };
    }

    init(root) {
        this.root = root;
        root.replaceChildren();
        root.className = 'three-viewer-timeline';
        root.innerHTML = `
            <div class="three-viewer-controls" role="group" aria-label="Viewer playback controls">
                <button type="button" data-action="play">Play</button>
                <button type="button" data-action="pause">Pause</button>
                <button type="button" data-action="stop">Stop</button>
                <label>Speed <select data-role="speed"><option value="0.25">0.25x</option><option value="0.5">0.5x</option><option value="1" selected>1x</option><option value="2">2x</option><option value="4">4x</option></select></label>
                <label><input type="checkbox" data-role="loop"> Loop</label>
                <span data-role="frame-readout">Frame 0 / 0</span>
                <button type="button" data-action="reset">Reset view</button>
            </div>
            <input data-role="frame" type="range" min="0" max="0" value="0" step="1" aria-label="Viewer frame">
        `;
        this.frameInput = root.querySelector('[data-role="frame"]');
        this.frameReadout = root.querySelector('[data-role="frame-readout"]');
        this.playButton = root.querySelector('[data-action="play"]');
        this.pauseButton = root.querySelector('[data-action="pause"]');
        this.stopButton = root.querySelector('[data-action="stop"]');
        this.speedInput = root.querySelector('[data-role="speed"]');
        this.loopInput = root.querySelector('[data-role="loop"]');
        this.frameInput.addEventListener('input', () => this.callbacks.onFrame?.(Number(this.frameInput.value)));
        this.playButton.addEventListener('click', () => this.callbacks.onPlay?.());
        this.pauseButton.addEventListener('click', () => this.callbacks.onPause?.());
        this.stopButton.addEventListener('click', () => this.callbacks.onStop?.());
        root.querySelector('[data-action="reset"]').addEventListener('click', () => this.callbacks.onReset?.());
        this.speedInput.addEventListener('change', () => this.callbacks.onSpeed?.(Number(this.speedInput.value)));
        this.loopInput.addEventListener('change', () => this.callbacks.onLoop?.(this.loopInput.checked));
    }

    setRange(totalFrames) {
        const maximum = Math.max(0, Number(totalFrames) - 1);
        this.frameInput.max = String(maximum);
        this.setFrame(0, totalFrames);
    }

    setFrame(frame, totalFrames = Number(this.frameInput?.max ?? 0) + 1) {
        if (!this.frameInput) return;
        const maximum = Math.max(0, Number(totalFrames) - 1);
        const current = Math.min(maximum, Math.max(0, Math.round(Number(frame) || 0)));
        this.frameInput.max = String(maximum);
        this.frameInput.value = String(current);
        this.frameReadout.textContent = `Frame ${current} / ${Math.max(0, Number(totalFrames) || 0)}`;
    }

    setPlaying(playing) {
        this.playButton?.toggleAttribute('disabled', Boolean(playing));
        this.pauseButton?.toggleAttribute('disabled', !playing);
    }

    destroy() {
        this.root?.replaceChildren();
        this.root = null;
    }
}
