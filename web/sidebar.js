import { JSONLoader } from './json_loader.js';

export class Sidebar {
    constructor() {
        this.container = null;
    }

    init(container) {
        this.container = container;
        this.render();
    }

    render(data = {}) {
        if (!this.container) return;
        const summary = Array.isArray(data.nodes)
            ? JSONLoader.summarizeScene(data)
            : { nodeCount: 0, cameraCount: 0, trajectoryCount: 0 };
        const cameras = countCollection(data.cameras ?? data.scene?.cameras);
        const trajectories = countCollection(data.trajectories ?? data.scene?.trajectories);
        this.container.innerHTML = `
            <h3>Project Explorer</h3>
            <ul>
                <li>Assets <span>${countCollection(data.assets)}</span></li>
                <li>Scenes <span>${data.scene ? 1 : 0}</span></li>
                <li>Nodes <span>${summary.nodeCount}</span></li>
                <li>Cameras <span>${cameras || summary.cameraCount}</span></li>
                <li>Trajectories <span>${trajectories || summary.trajectoryCount}</span></li>
            </ul>
        `;
    }
}

function countCollection(collection) {
    if (Array.isArray(collection)) return collection.length;
    if (collection && typeof collection === 'object') return Object.keys(collection).length;
    return 0;
}
