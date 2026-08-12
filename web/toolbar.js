export class Toolbar {
    constructor() {
        this.container = null;
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
                <button>Load JSON</button>
                <button>Save Workspace</button>
                <button>Settings</button>
            </div>
        `;
    }
}
