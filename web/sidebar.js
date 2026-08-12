export class Sidebar {
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
            <h3>Project Explorer</h3>
            <ul>
                <li>Assets</li>
                <li>Scenes</li>
                <li>Trajectories</li>
            </ul>
        `;
    }
}
