export class Toolbar {
    constructor({
        onLoadJSON = null,
        onResetView = null,
        onUndo = null,
        onRedo = null,
        onInsert = null,
        onDuplicate = null,
        onDelete = null,
        onFramePrevious = null,
        onFrameNext = null,
        onPlay = null,
        onPause = null,
        onStop = null,
        onLoop = null,
        onFps = null,
        onSpeed = null,
        onReverse = null,
        onTrajectoryVisibility = null,
        onTrajectoryGhost = null,
        onTrajectoryHistory = null,
        onTrajectoryColor = null,
        onTrajectoryThickness = null,
        onTrajectorySmoothing = null,
    } = {}) {
        this.container = null;
        this.onLoadJSON = onLoadJSON;
        this.onResetView = onResetView;
        this.onUndo = onUndo;
        this.onRedo = onRedo;
        this.onInsert = onInsert;
        this.onDuplicate = onDuplicate;
        this.onDelete = onDelete;
        this.onFramePrevious = onFramePrevious;
        this.onFrameNext = onFrameNext;
        this.onPlay = onPlay;
        this.onPause = onPause;
        this.onStop = onStop;
        this.onLoop = onLoop;
        this.onFps = onFps;
        this.onSpeed = onSpeed;
        this.onReverse = onReverse;
        this.onTrajectoryVisibility = onTrajectoryVisibility;
        this.onTrajectoryGhost = onTrajectoryGhost;
        this.onTrajectoryHistory = onTrajectoryHistory;
        this.onTrajectoryColor = onTrajectoryColor;
        this.onTrajectoryThickness = onTrajectoryThickness;
        this.onTrajectorySmoothing = onTrajectorySmoothing;
    }

    init(container) {
        this.container = container;
        this.render();
    }

    render() {
        if (!this.container) return;
        this.container.innerHTML = `
            <div style="font-weight: bold; color: var(--accent);">Fly Studio Web</div>
            <div style="margin-left: 20px;">
                <button id="load-json-button" type="button">Load JSON</button>
                <input id="load-json-input" type="file" accept=".json,application/json" hidden>
                <button id="reset-view-button" type="button">Reset View</button>
                <button id="undo-button" type="button">Undo</button>
                <button id="redo-button" type="button">Redo</button>
                <button id="insert-keyframe-button" type="button">Insert Keyframe</button>
                <button id="duplicate-keyframe-button" type="button">Duplicate</button>
                <button id="delete-keyframe-button" type="button">Delete</button>
                <button id="frame-previous-button" type="button">Frame -</button>
                <button id="frame-next-button" type="button">Frame +</button>
                <button id="play-button" type="button">Play</button>
                <button id="pause-button" type="button">Pause</button>
                <button id="stop-button" type="button">Stop</button>
                <label>Loop <input id="loop-input" type="checkbox"></label>
                <label>FPS <input id="fps-input" type="number" min="1" step="1" value="30"></label>
                <label>Speed <input id="speed-input" type="number" min="0.1" step="0.1" value="1"></label>
                <label>Reverse <input id="reverse-input" type="checkbox"></label>
                <label>Trail <input id="trajectory-visible-input" type="checkbox" checked></label>
                <label>Ghost <input id="trajectory-ghost-input" type="checkbox" checked></label>
                <label>History <input id="trajectory-history-input" type="checkbox" checked></label>
                <label>Trail Color <input id="trajectory-color-input" type="color" value="#58c4dd"></label>
                <label>Trail Width <input id="trajectory-thickness-input" type="number" min="1" step="1" value="2"></label>
                <label>Smooth <input id="trajectory-smoothing-input" type="checkbox"></label>
                <button>Save Workspace</button>
                <button>Settings</button>
            </div>
        `;

        const loadButton = this.container.querySelector('#load-json-button');
        const fileInput = this.container.querySelector('#load-json-input');
        const resetViewButton = this.container.querySelector('#reset-view-button');
        const undoButton = this.container.querySelector('#undo-button');
        const redoButton = this.container.querySelector('#redo-button');
        const insertButton = this.container.querySelector('#insert-keyframe-button');
        const duplicateButton = this.container.querySelector('#duplicate-keyframe-button');
        const deleteButton = this.container.querySelector('#delete-keyframe-button');
        const framePreviousButton = this.container.querySelector('#frame-previous-button');
        const frameNextButton = this.container.querySelector('#frame-next-button');
        const playButton = this.container.querySelector('#play-button');
        const pauseButton = this.container.querySelector('#pause-button');
        const stopButton = this.container.querySelector('#stop-button');
        const loopInput = this.container.querySelector('#loop-input');
        const fpsInput = this.container.querySelector('#fps-input');
        const speedInput = this.container.querySelector('#speed-input');
        const reverseInput = this.container.querySelector('#reverse-input');
        const trajectoryVisibleInput = this.container.querySelector('#trajectory-visible-input');
        const trajectoryGhostInput = this.container.querySelector('#trajectory-ghost-input');
        const trajectoryHistoryInput = this.container.querySelector('#trajectory-history-input');
        const trajectoryColorInput = this.container.querySelector('#trajectory-color-input');
        const trajectoryThicknessInput = this.container.querySelector('#trajectory-thickness-input');
        const trajectorySmoothingInput = this.container.querySelector('#trajectory-smoothing-input');
        loadButton.addEventListener('click', () => fileInput.click());
        resetViewButton.addEventListener('click', () => {
            if (this.onResetView) this.onResetView();
        });
        undoButton.addEventListener('click', () => { if (this.onUndo) this.onUndo(); });
        redoButton.addEventListener('click', () => { if (this.onRedo) this.onRedo(); });
        insertButton.addEventListener('click', () => { if (this.onInsert) this.onInsert(); });
        duplicateButton.addEventListener('click', () => { if (this.onDuplicate) this.onDuplicate(); });
        deleteButton.addEventListener('click', () => { if (this.onDelete) this.onDelete(); });
        framePreviousButton.addEventListener('click', () => { if (this.onFramePrevious) this.onFramePrevious(); });
        frameNextButton.addEventListener('click', () => { if (this.onFrameNext) this.onFrameNext(); });
        playButton.addEventListener('click', () => { if (this.onPlay) this.onPlay(); });
        pauseButton.addEventListener('click', () => { if (this.onPause) this.onPause(); });
        stopButton.addEventListener('click', () => { if (this.onStop) this.onStop(); });
        loopInput.addEventListener('change', () => { if (this.onLoop) this.onLoop(loopInput.checked); });
        fpsInput.addEventListener('change', () => { if (this.onFps) this.onFps(fpsInput.value); });
        speedInput.addEventListener('change', () => { if (this.onSpeed) this.onSpeed(speedInput.value); });
        reverseInput.addEventListener('change', () => { if (this.onReverse) this.onReverse(reverseInput.checked); });
        trajectoryVisibleInput.addEventListener('change', () => { if (this.onTrajectoryVisibility) this.onTrajectoryVisibility(trajectoryVisibleInput.checked); });
        trajectoryGhostInput.addEventListener('change', () => { if (this.onTrajectoryGhost) this.onTrajectoryGhost(trajectoryGhostInput.checked); });
        trajectoryHistoryInput.addEventListener('change', () => { if (this.onTrajectoryHistory) this.onTrajectoryHistory(trajectoryHistoryInput.checked); });
        trajectoryColorInput.addEventListener('change', () => { if (this.onTrajectoryColor) this.onTrajectoryColor(trajectoryColorInput.value); });
        trajectoryThicknessInput.addEventListener('change', () => { if (this.onTrajectoryThickness) this.onTrajectoryThickness(trajectoryThicknessInput.value); });
        trajectorySmoothingInput.addEventListener('change', () => { if (this.onTrajectorySmoothing) this.onTrajectorySmoothing(trajectorySmoothingInput.checked); });
        fileInput.addEventListener('change', async () => {
            const [file] = fileInput.files;
            if (file && this.onLoadJSON) await this.onLoadJSON(file);
            fileInput.value = '';
        });
    }

    updatePlaybackState(workspace) {
        if (!this.container) return;
        const state = workspace.playbackState;
        const playButton = this.container.querySelector('#play-button');
        const pauseButton = this.container.querySelector('#pause-button');
        const loopInput = this.container.querySelector('#loop-input');
        const fpsInput = this.container.querySelector('#fps-input');
        const speedInput = this.container.querySelector('#speed-input');
        const reverseInput = this.container.querySelector('#reverse-input');
        const trajectoryVisibleInput = this.container.querySelector('#trajectory-visible-input');
        const trajectoryGhostInput = this.container.querySelector('#trajectory-ghost-input');
        const trajectoryHistoryInput = this.container.querySelector('#trajectory-history-input');
        const trajectoryColorInput = this.container.querySelector('#trajectory-color-input');
        const trajectoryThicknessInput = this.container.querySelector('#trajectory-thickness-input');
        const trajectorySmoothingInput = this.container.querySelector('#trajectory-smoothing-input');
        if (playButton) playButton.disabled = state === 'Playing';
        if (pauseButton) pauseButton.disabled = state !== 'Playing';
        if (loopInput) loopInput.checked = Boolean(workspace.loop);
        if (fpsInput && document.activeElement !== fpsInput) fpsInput.value = workspace.fps;
        if (speedInput && document.activeElement !== speedInput) speedInput.value = workspace.speed;
        if (reverseInput) reverseInput.checked = Boolean(workspace.reverse);
        const settings = workspace.trajectorySettings ?? {};
        if (trajectoryVisibleInput) trajectoryVisibleInput.checked = settings.visible !== false;
        if (trajectoryGhostInput) trajectoryGhostInput.checked = settings.ghostTrail !== false;
        if (trajectoryHistoryInput) trajectoryHistoryInput.checked = settings.historyTrail !== false;
        if (trajectoryColorInput && settings.color) trajectoryColorInput.value = settings.color;
        if (trajectoryThicknessInput && settings.thickness) trajectoryThicknessInput.value = settings.thickness;
        if (trajectorySmoothingInput) trajectorySmoothingInput.checked = Boolean(settings.smoothing);
    }
}
