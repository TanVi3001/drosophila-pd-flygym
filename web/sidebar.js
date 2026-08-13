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
            <ul class="project-summary">
                <li>Assets <span>${countCollection(data.assets)}</span></li>
                <li>Scenes <span>${data.scene ? 1 : 0}</span></li>
                <li>Nodes <span>${summary.nodeCount}</span></li>
                <li>Cameras <span>${cameras || summary.cameraCount}</span></li>
                <li>Trajectories <span>${trajectories || summary.trajectoryCount}</span></li>
            </ul>
            <section class="scene-tree-panel" aria-labelledby="scene-tree-title">
                <h4 id="scene-tree-title"></h4>
                <div class="scene-tree-content"></div>
            </section>
        `;

        const sceneTitle = this.container.querySelector('#scene-tree-title');
        sceneTitle.textContent = getSceneLabel(data.scene);
        const treeContent = this.container.querySelector('.scene-tree-content');
        const nodes = Array.isArray(data.nodes) ? data.nodes : [];
        if (nodes.length === 0) {
            const emptyState = document.createElement('p');
            emptyState.className = 'scene-tree-empty';
            emptyState.textContent = 'No scene nodes loaded.';
            treeContent.appendChild(emptyState);
            return;
        }

        const tree = document.createElement('ul');
        tree.className = 'scene-tree';
        appendNodes(tree, nodes);
        treeContent.appendChild(tree);
    }
}

function appendNodes(list, nodes) {
    nodes.forEach((node) => {
        const element = createNodeElement(node);
        if (element) list.appendChild(element);
    });
}

function createNodeElement(node) {
    if (!node || typeof node !== 'object' || Array.isArray(node)) return null;

    const item = document.createElement('li');
    item.className = 'scene-tree-node';
    const children = Array.isArray(node.children)
        ? node.children.filter((child) => child && typeof child === 'object')
        : [];

    if (children.length === 0) {
        item.textContent = getNodeLabel(node);
        return item;
    }

    const details = document.createElement('details');
    details.open = true;
    const label = document.createElement('summary');
    label.textContent = getNodeLabel(node);
    details.appendChild(label);

    const childList = document.createElement('ul');
    appendNodes(childList, children);
    details.appendChild(childList);
    item.appendChild(details);
    return item;
}

function getNodeLabel(node) {
    return String(node.name ?? node.id ?? node.type ?? node.kind ?? 'Unnamed node');
}

function getSceneLabel(scene) {
    if (scene && typeof scene === 'object' && scene.name) return String(scene.name);
    return 'Scene';
}

function countCollection(collection) {
    if (Array.isArray(collection)) return collection.length;
    if (collection && typeof collection === 'object') return Object.keys(collection).length;
    return 0;
}
