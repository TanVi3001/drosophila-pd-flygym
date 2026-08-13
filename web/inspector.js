export class Inspector {
    constructor(workspace) {
        this.workspace = workspace;
        this.container = null;
    }

    init(container) {
        this.container = container;
        this.render();
    }

    render() {
        if (!this.container) return;

        this.container.replaceChildren();
        const heading = document.createElement('h3');
        heading.textContent = 'Inspector';
        this.container.appendChild(heading);

        const node = this.workspace.selectedNode;
        if (!node) {
            const emptyState = document.createElement('p');
            emptyState.className = 'inspector-empty';
            emptyState.textContent = 'No node selected';
            this.container.appendChild(emptyState);
            return;
        }

        const details = document.createElement('dl');
        appendDetail(details, 'Name', getNodeName(node));
        appendDetail(details, 'ID', getOptionalValue(node.id));
        appendDetail(details, 'Type', getOptionalValue(node.type ?? node.kind));
        appendDetail(details, 'Parent', getParentLabel(this.workspace.data, node));
        appendDetail(details, 'Children count', getChildren(node).length);
        this.container.appendChild(details);

        if (node.metadata !== undefined && node.metadata !== null) {
            const metadataHeading = document.createElement('h4');
            metadataHeading.textContent = 'Metadata';
            this.container.appendChild(metadataHeading);

            const metadata = document.createElement('pre');
            metadata.className = 'inspector-metadata';
            metadata.textContent = formatMetadata(node.metadata);
            this.container.appendChild(metadata);
        }
    }
}

function appendDetail(list, label, value) {
    const term = document.createElement('dt');
    term.textContent = label;
    const description = document.createElement('dd');
    description.textContent = String(value);
    list.appendChild(term);
    list.appendChild(description);
}

function getNodeName(node) {
    return node.name ?? node.id ?? node.type ?? node.kind ?? 'Unnamed node';
}

function getOptionalValue(value) {
    return value === undefined || value === null || value === ''
        ? 'Not available'
        : value;
}

function getChildren(node) {
    return Array.isArray(node.children) ? node.children : [];
}

function getParentLabel(data, target) {
    const parent = findParent(Array.isArray(data.nodes) ? data.nodes : [], target);
    if (!parent) return 'Scene root';
    return getNodeName(parent);
}

function findParent(nodes, target, parent = null) {
    for (const node of nodes) {
        if (!node || typeof node !== 'object') continue;
        if (node === target) return parent;
        const children = getChildren(node);
        const result = findParent(children, target, node);
        if (result) return result;
    }
    return null;
}

function formatMetadata(metadata) {
    if (typeof metadata === 'object') {
        try {
            return JSON.stringify(metadata, null, 2);
        } catch (error) {
            return String(metadata);
        }
    }
    return String(metadata);
}
