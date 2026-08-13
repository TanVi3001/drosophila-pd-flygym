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
        fileInput.addEventListener('change', async () => {
            const [file] = fileInput.files;
            if (file && this.onLoadJSON) await this.onLoadJSON(file);
            fileInput.value = '';
        });
    }
}
