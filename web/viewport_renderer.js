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
        this.cameraOffsetX = 0;
        this.cameraOffsetY = 0;
        this.zoom = 1;
        this.isPanning = false;
        this.spacePressed = false;
        this.spaceUsedForPan = false;
        this.lastPointerX = 0;
        this.lastPointerY = 0;
        this.keyDownHandler = (event) => this.handleKeyDown(event);
        this.keyUpHandler = (event) => this.handleKeyUp(event);
    }

    init(container) {
        this.container = container;
        this.canvas = document.createElement('canvas');
        this.canvas.className = 'viewport-canvas';
        this.canvas.setAttribute('aria-label', 'Scene viewport');
        this.container.replaceChildren(this.canvas);
        this.context = this.canvas.getContext('2d');
        this.canvas.addEventListener('wheel', (event) => this.handleWheel(event), { passive: false });
        this.canvas.addEventListener('pointerdown', (event) => this.handlePointerDown(event));
        this.canvas.addEventListener('pointermove', (event) => this.handlePointerMove(event));
        this.canvas.addEventListener('pointerup', (event) => this.handlePointerUp(event));
        this.canvas.addEventListener('pointercancel', (event) => this.handlePointerUp(event));
        this.canvas.addEventListener('dblclick', () => this.focusSelectedNode());
        window.addEventListener('keydown', this.keyDownHandler);
        window.addEventListener('keyup', this.keyUpHandler);

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

    resetView() {
        this.cameraOffsetX = 0;
        this.cameraOffsetY = 0;
        this.zoom = 1;
        this.render();
    }

    focusSelectedNode() {
        const selectedNode = this.workspace.selectedNode;
        const nodes = Array.isArray(this.workspace.data?.nodes)
            ? this.workspace.data.nodes
            : [];
        if (!selectedNode || nodes.length === 0) return;

        const layout = layoutNodes(nodes, this.width, this.height);
        const position = layout.positionByNode.get(selectedNode);
        if (!position) return;

        this.cameraOffsetX = -this.zoom * (position.x - this.width / 2);
        this.cameraOffsetY = -this.zoom * (position.y - this.height / 2);
        this.render();
    }

    consumeSpacePan() {
        const usedForPan = this.spaceUsedForPan;
        this.spaceUsedForPan = false;
        return usedForPan;
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
        const currentFrame = Number.isInteger(this.workspace.currentFrame)
            ? this.workspace.currentFrame
            : 0;
        if (nodes.length === 0) {
            this.drawMessage('No Scene Loaded');
            return;
        }

        const layout = layoutNodes(nodes, this.width, this.height);
        this.context.save();
        this.applyCameraTransform();
        this.drawLinks(layout);
        this.drawNodes(layout, this.workspace.selectedNode, currentFrame);
        this.context.restore();
    }

    applyCameraTransform() {
        this.context.translate(
            this.width / 2 + this.cameraOffsetX,
            this.height / 2 + this.cameraOffsetY,
        );
        this.context.scale(this.zoom, this.zoom);
        this.context.translate(-this.width / 2, -this.height / 2);
    }

    handleWheel(event) {
        event.preventDefault();
        const factor = Math.exp(-event.deltaY * 0.001);
        this.zoomAt(factor, event.offsetX, event.offsetY);
    }

    zoomAt(factor, x, y) {
        const nextZoom = clamp(this.zoom * factor, 0.25, 4);
        const centerX = this.width / 2;
        const centerY = this.height / 2;
        const worldX = centerX + (x - centerX - this.cameraOffsetX) / this.zoom;
        const worldY = centerY + (y - centerY - this.cameraOffsetY) / this.zoom;
        this.zoom = nextZoom;
        this.cameraOffsetX = x - centerX - this.zoom * (worldX - centerX);
        this.cameraOffsetY = y - centerY - this.zoom * (worldY - centerY);
        this.render();
    }

    handlePointerDown(event) {
        const middleButton = event.button === 1;
        const spaceDrag = event.button === 0 && this.spacePressed;
        if (!middleButton && !spaceDrag) return;

        event.preventDefault();
        this.isPanning = true;
        this.spaceUsedForPan = this.spaceUsedForPan || spaceDrag;
        this.lastPointerX = event.clientX;
        this.lastPointerY = event.clientY;
        this.canvas.setPointerCapture(event.pointerId);
    }

    handlePointerMove(event) {
        if (!this.isPanning) return;
        event.preventDefault();
        this.cameraOffsetX += event.clientX - this.lastPointerX;
        this.cameraOffsetY += event.clientY - this.lastPointerY;
        this.lastPointerX = event.clientX;
        this.lastPointerY = event.clientY;
        this.render();
    }

    handlePointerUp(event) {
        if (!this.isPanning) return;
        this.isPanning = false;
        if (this.canvas.hasPointerCapture(event.pointerId)) {
            this.canvas.releasePointerCapture(event.pointerId);
        }
    }

    handleKeyDown(event) {
        if (event.code === 'Space') this.spacePressed = true;
    }

    handleKeyUp(event) {
        if (event.code === 'Space') this.spacePressed = false;
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

    drawNodes(layout, selectedNode, currentFrame) {
        // The frame is intentionally read-only here; playback will use it later.
        void currentFrame;
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

function clamp(value, minimum, maximum) {
    return Math.min(maximum, Math.max(minimum, value));
}
