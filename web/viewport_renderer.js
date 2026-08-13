const BACKGROUND = '#0b0b0b';
const LINK_COLOR = '#5f6b78';
const NODE_COLOR = '#49a6d8';
const SELECTED_COLOR = '#ffcc66';
const TEXT_COLOR = '#d8dee5';

export class ViewportRenderer {
    constructor(workspace) {
        this.workspace = workspace;
        this.container = null;
        this.canvas = null;
        this.context = null;
        this.resizeObserver = null;
        this.resizeHandler = () => this.resize();
        this.devicePixelRatio = 1;
        this.width = 0;
        this.height = 0;
    }

    init(container) {
        this.container = container;
        this.canvas = document.createElement('canvas');
        this.canvas.className = 'viewport-canvas';
        this.canvas.setAttribute('aria-label', 'Scene viewport');
        this.container.replaceChildren(this.canvas);
        this.context = this.canvas.getContext('2d');

        if (typeof ResizeObserver !== 'undefined') {
            this.resizeObserver = new ResizeObserver(() => this.resize());
            this.resizeObserver.observe(this.container);
        } else {
            window.addEventListener('resize', this.resizeHandler);
        }

        this.resize();
    }

    clear() {
        if (!this.context) return;
        this.context.save();
        this.context.setTransform(1, 0, 0, 1, 0, 0);
        this.context.fillStyle = BACKGROUND;
        this.context.fillRect(0, 0, this.canvas.width, this.canvas.height);
        this.context.restore();
    }

    resize() {
        if (!this.container || !this.canvas || !this.context) return;

        const width = Math.max(1, Math.floor(this.container.clientWidth));
        const height = Math.max(1, Math.floor(this.container.clientHeight));
        const pixelRatio = Math.max(1, window.devicePixelRatio || 1);
        const changed = width !== this.width
            || height !== this.height
            || pixelRatio !== this.devicePixelRatio;

        if (!changed) return;

        this.width = width;
        this.height = height;
        this.devicePixelRatio = pixelRatio;
        this.canvas.width = Math.floor(width * pixelRatio);
        this.canvas.height = Math.floor(height * pixelRatio);
        this.canvas.style.width = `${width}px`;
        this.canvas.style.height = `${height}px`;
        this.context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
        this.render();
    }

    render() {
        if (!this.context || !this.canvas) return;

        this.clear();

        const nodes = Array.isArray(this.workspace.data?.nodes)
            ? this.workspace.data.nodes
            : [];
        if (nodes.length === 0) {
            this.drawMessage('No Scene Loaded');
            return;
        }

        const layout = layoutNodes(nodes, this.width, this.height);
        this.drawLinks(layout);
        this.drawNodes(layout, this.workspace.selectedNode);
    }

    drawMessage(message) {
        this.context.fillStyle = TEXT_COLOR;
        this.context.font = '16px monospace';
        this.context.textAlign = 'center';
        this.context.textBaseline = 'middle';
        this.context.fillText(message, this.width / 2, this.height / 2);
    }

    drawLinks(layout) {
        this.context.strokeStyle = LINK_COLOR;
        this.context.lineWidth = 1.5;
        this.context.beginPath();
        layout.forEach(({ node, parent }) => {
            if (!parent) return;
            const parentPosition = layout.positionByNode.get(parent);
            const position = layout.positionByNode.get(node);
            if (!parentPosition || !position) return;
            this.context.moveTo(parentPosition.x, parentPosition.y);
            this.context.lineTo(position.x, position.y);
        });
        this.context.stroke();
    }

    drawNodes(layout, selectedNode) {
        this.context.font = '12px sans-serif';
        this.context.textAlign = 'left';
        this.context.textBaseline = 'middle';

        layout.forEach(({ node, x, y }) => {
            const selected = node === selectedNode;
            this.context.beginPath();
            this.context.arc(x, y, selected ? 8 : 6, 0, Math.PI * 2);
            this.context.fillStyle = selected ? SELECTED_COLOR : NODE_COLOR;
            this.context.fill();
            if (selected) {
                this.context.strokeStyle = '#ffffff';
                this.context.lineWidth = 2;
                this.context.stroke();
            }

            this.context.fillStyle = TEXT_COLOR;
            this.context.fillText(getNodeLabel(node), x + 12, y);
        });
    }
}

function layoutNodes(nodes, width, height) {
    const entries = [];
    let leafCount = 0;
    let maxDepth = 0;

    function collect(node, parent, depth) {
        if (!node || typeof node !== 'object' || Array.isArray(node)) return null;
        maxDepth = Math.max(maxDepth, depth);
        const entry = { node, parent, depth, leafIndex: null, logicalY: 0, x: 0, y: 0 };
        entries.push(entry);
        const children = Array.isArray(node.children) ? node.children : [];
        const childEntries = children
            .map((child) => collect(child, node, depth + 1))
            .filter(Boolean);

        if (childEntries.length === 0) {
            entry.leafIndex = leafCount;
            entry.logicalY = leafCount;
            leafCount += 1;
        } else {
            entry.logicalY = childEntries.reduce((sum, child) => sum + child.logicalY, 0)
                / childEntries.length;
        }
        return entry;
    }

    nodes.forEach((node) => collect(node, null, 0));
    const horizontalPadding = 42;
    const verticalPadding = 32;
    const horizontalStep = maxDepth > 0
        ? (Math.max(horizontalPadding, width - horizontalPadding * 2) / maxDepth)
        : 0;
    const verticalStep = leafCount > 1
        ? (Math.max(verticalPadding, height - verticalPadding * 2) / (leafCount - 1))
        : 0;
    const positionByNode = new Map();

    entries.forEach((entry) => {
        entry.x = horizontalPadding + entry.depth * horizontalStep;
        entry.y = leafCount > 1
            ? verticalPadding + entry.logicalY * verticalStep
            : height / 2;
        positionByNode.set(entry.node, { x: entry.x, y: entry.y });
    });

    return Object.assign(entries, { positionByNode });
}

function getNodeLabel(node) {
    return String(node.name ?? node.id ?? node.type ?? node.kind ?? 'Unnamed node');
}
