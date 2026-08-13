export class Toolbar {
    constructor({ onLoadJSON = null } = {}) {
        this.container = null;
        this.onLoadJSON = onLoadJSON;
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
                <button>Save Workspace</button>
                <button>Settings</button>
            </div>
        `;

        const loadButton = this.container.querySelector('#load-json-button');
        const fileInput = this.container.querySelector('#load-json-input');
        loadButton.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', async () => {
            const [file] = fileInput.files;
            if (file && this.onLoadJSON) await this.onLoadJSON(file);
            fileInput.value = '';
        });
    }
}
